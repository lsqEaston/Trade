"""
结合kungfu的add_time_interval()时间间隔回调使用
1.用于读取某个时间段所有策略的目标持仓数据，然后将该持仓数据整合，传入到kungfu的交易函数中；
2.kungfu交易函数执行完毕后，获取对应的交易数据，将该交易数据返回；
"""

from multiprocessing import Queue
# from kungfu.wingchun.constants import Side, Offset, Direction, PriceType, OrderStatus, Exchange
from DataType.orderType import *
import kungfu.yijinjing.time as kft
import pandas as pd


'''
总体流程：
1.on_quote计算策略交易信号，交易信号按每分钟汇总，汇总到TargetPosHander中；
2. 每固定周期调用add_time_interval()，将TargetPosHander中的交易信号传入到kungfu的交易函数中；
3.交易函数执行完毕后，获取对应的交易数据，将该交易数据返回；

'''




class TargetPosHander:
    def __init__(self):
        # 流程处理类
        self.process = ProcessGenerator()
        # 多个策略传入
        self.targets = Queue()
        self.resTargets=[]
        # 通过kungfu下单前的targets
        self.pre_targets = {}
        # 下单完毕后的targets
        self.post_targets = {}
        # 收到成交信息后的结果保存
        self.res= {'target':[], 'realTarget':[]}

        # DEBUG
        self.__DEBUG=True
        # delay
        self.order_follow=OrderFollow.Append
        self.__DELAY = 30 * kft.NANO_PER_SECOND
        self.follow_targets = {}

    def add_target(self, target: Target):
        self.targets.put(target)

    # 在每分钟末计算的时候，targets所有内容都要清空
    def __get_targets(self):
        lst = []
        while not self.targets.empty():
            lst.append(self.targets.get())
        return lst


    #根据Target中的策略id，合约代码，买卖方向，开平方向，计算多个Target的nominal
    def calc_order_nominal(self):
        # 初始化
        targets = self.__get_targets()
        targets = pd.DataFrame(targets)
        # 计算每个策略的nominal总和
        # strt_nominal = targets.groupby(['strategy_id', 'instrument_id', 'exchange', 'side', 'offset'])['nominal'].sum()
        strt_nominal = targets.groupby(['strategy_id', 'instrument_id', 'exchange', 'side', 'offset']).agg({'nominal':'sum', 'limit_price':'mean'})
        # 计算每个合约的nominal总和
        # total_nominal = targets.groupby(['instrument_id', 'exchange', 'side', 'offset'])['nominal'].sum()
        total_nominal = targets.groupby(['instrument_id', 'exchange', 'side', 'offset']).agg({'nominal':'sum', 'limit_price':'mean'})
        return total_nominal, strt_nominal


    # 计算周期内所有策略的权重
    def calc_weights(self, total_nominal:pd.DataFrame, strt_nominal:pd.DataFrame):
        # 计算权重
        weights=strt_nominal.nominal/total_nominal.nominal
        weights_df = pd.concat([strt_nominal,weights.rename('weights')], axis=1)

        for index, df in weights_df.iterrows():
            orderTarget = Target(index[0], index[1], index[2], Side(index[3]), Offset(index[4]), df.nominal, df.limit_price)
            orderTarget.weights = df.weights
            self.resTargets.append(orderTarget)


    # 初始化总订单
    def add_total_orders(self, total_nominal:pd.DataFrame):
        for index, df in total_nominal.iterrows():
            if index[0] not in self.pre_targets.keys():
                self.pre_targets[index[0]] = []
            self.pre_targets[index[0]].append(RealTarget(index[0], index[1], Side(index[2]), Offset(index[3]), df.nominal, df.limit_price))



    # 获取已成交后的信息,根据成交前的权重和已成交的数量和价格，计算成交后的权重
    def collect_trade(self,realTarget:RealTarget):
        for target in self.resTargets:
            if target == realTarget: #重载operator==()  ->(instrument_id, side, offset)
                target.order_id = realTarget.order_id
                target.real_nominal = target.weights * realTarget.real_nominal
                self.res['target'].append(target)




    # 定时回调下单，需要确定交易价格
    def update_order_timer(self, context, order_targets:dict[str,list[RealTarget]], price_type:PriceType, source:str, account:str):
        if len(order_targets) > 0:
            delete_key = []
            for instrumentID, realTargetlist in order_targets.items():
                # realTargetlist_iter = realTargetlist
                for realTarget in reversed(realTargetlist):
                    vol = (realTarget.nominal // realTarget.limit_price) if (realTarget.nominal // realTarget.limit_price >0) else 0
                    if vol>0:
                        order_id = context.insert_order(instrumentID, realTarget.exchange, source, account,
                                                        realTarget.limit_price, vol, price_type,
                                                        realTarget.side, realTarget.offset)
                        if order_id > 0:
                            # 第一个下单完毕后，可以开始接受trade回调信息
                            if self.process.value == OrderProcess.Order:
                                self.process.next()

                            realTarget.order_id = order_id
                            self.post_targets[realTarget.order_id] = realTarget

                            # 下单成功后，如果是Append或者Drop，需要设置延时取消订单
                            if self.order_follow == OrderFollow.Drop or self.order_follow == OrderFollow.Append:
                                context.add_timer(context.now() + self.__DELAY,
                                                  lambda context, event: self.cancel_order(context, order_id))

                            if self.__DEBUG:
                                context.log.info(f"send to kungfu sucessful，info：{realTarget}")

                    # 下单完毕后，删除pre_targets中的相关合约信息:所有合约下单完毕后再删除-->节约内存+缩短下单时间
                    # vol==0:该合约无需下单，同样进行剔除
                    order_targets[instrumentID].remove(realTarget)
                    if len(order_targets[instrumentID]) == 0:
                        delete_key.append(instrumentID)

            for instrumentID in delete_key:
                del order_targets[instrumentID]


        return order_targets


    # 下单-->定时下单-->下单完毕后会更新post_targets列表中的realTarget类
    def order_by_timer(self, context, price_type:PriceType, source:str, account:str):
        # 分组聚合后执行下单交易
        if self.process.value == OrderProcess.Order or self.process.value == OrderProcess.Trade:
            self.update_order_timer(context, self.pre_targets, price_type, source, account)
            self.update_order_timer(context, self.follow_targets, price_type, source, account)



    def clear(self):
        self.resTargets = []
        # self.pre_targets = {}
        # self.post_targets = {}

    # on_order返回订单信息（无论是否成交）
    def update_by_order(self, context, order):
        if order.order_id in self.post_targets.keys():
            if order.status == OrderStatus.Cancelled:       #撤单：暂时不操作
                '''
                do something for cancel
                '''
                if self.order_follow == OrderFollow.Append:
                    # Append:保留到下一轮的买入队列
                    if order.instrument_id not in self.follow_targets.keys():
                        self.follow_targets[order.instrument_id] = []
                    self.post_targets[order.order_id].order_id=None
                    # setattr(self.post_targets[order.order_id], 'delay', True) # 设置保留标志
                    self.follow_targets[order.instrument_id].append(self.post_targets[order.order_id])

                # drop / Append :直接丢弃该合约的下单
                del self.post_targets[order.order_id]

            elif order.status == OrderStatus.Error:           #错误：暂时不操作
                '''
                do something for error
                '''
                del self.post_targets[order.order_id]
            elif order.status == OrderStatus.Lost:            #丢失：暂时不操作
                '''
                do something for lost
                '''
                del self.post_targets[order.order_id]

            # elif order.status == OrderStatus.PartialFilledNotActive:          #部成部撤：暂时不操作
            #     del self.post_targets[order.order_id]


    # on_trade返回成交回报后的信息-->更新成交后的策略信息
    def update_by_trade(self, context, trade):
        realTarget = self.post_targets[trade.order_id]
        realTarget.real_nominal = trade.volume * trade.price
        realTarget.commission = trade.commission
        realTarget.tax = trade.tax
        self.collect_trade(realTarget)
        self.res['realTarget'].append(realTarget)

        context.log.info(f"{trade.instrument_id}已成交, 成交信息:{realTarget}")

        del self.post_targets[trade.order_id]

        if self.process.value==OrderProcess.Trade and len(self.post_targets)==0 and len(self.pre_targets)==0:
            context.log.info("get all deal, can reorder")
            self.clear()
            self.process.reset()
            # self.process = self.start()


    def to_exchange(self, context, price_type:PriceType,source:str, account:str):
        context.log.info("initialize all strategy orders")
        if not self.targets.empty():
            # step1:策略订单分发计算
            total_nominal, strt_nominal = self.calc_order_nominal()  # 计算策略和账户合约nominal
            self.calc_weights(total_nominal, strt_nominal)  # 计算权重
            self.add_total_orders(total_nominal)  # 初始化总订单
            self.process.next()
            # step2:根据价格下单
            if self.__DEBUG:
                context.log.info("orders send to Kungfu")
            self.order_by_timer(context, price_type, source, account)

    def callback_timer_init(self, context, price_type:PriceType, source:str, account:str)->None:
        if self.process.value == OrderProcess.collect:
            self.to_exchange(context, price_type, source, account)
            return
        if self.process.value == OrderProcess.Order:
            context.log.info("ordering......from Kungfu to Exchange")
        if self.process.value == OrderProcess.Trade:
            # context.log.info(f'pre_targes numbers:{len(self.pre_targets)}')
            # context.log.info(f'post_targes numbers:{len(self.post_targets)}')
            if len(self.post_targets)==0 and len(self.pre_targets)==0:
                context.log.info("get all deal, can reorder")
                self.clear()
                self.process.reset()
                self.to_exchange(context, price_type, source, account)
            else:
                context.log.info("waiting......get deal callback from Exchange")

    def cancel_order(self, context, order_id):
        action_id = context.cancel_order(order_id)
        if action_id>0:
            # 若已成交，则会出现error 25错误：订单无法找到，此错误可忽略
            context.log.info(f"cancel order_id: {order_id}")



    # 成交回调时调用
    def callback_trade(self, context, trade):
        self.update_by_trade(context, trade)

    # process生成器
    def gen_process(self):
        yield OrderProcess.collect
        yield OrderProcess.Order
        yield OrderProcess.Trade

        # 未成交订单
        # unFilledIDs = self.handle_unTrade(context, orderIDs)



class ProcessGenerator:
    """
    用于生成 targetPosition 处理流程
    """
    def __init__(self):
        self.__process = self.gen_process()
        self.value = next(self.__process)

    @staticmethod
    def gen_process():
        yield OrderProcess.collect
        yield OrderProcess.Order
        yield OrderProcess.Trade

    def next(self):
        self.value = next(self.__process)

    def get_process(self):
        return self.__process

    def set_process(self):
        self.__process = self.gen_process()
        self.value = None

    def reset(self):
        self.__process = self.gen_process()
        self.value = next(self.__process)



# kungfu 下单
# context.insert_order(instrument_id, exchange_id, source_id, account_id, limit_price, volume, priceType, side, offset)
# context.insert_order("rb1906", Exchange.SHFE, "sim", "simTest", 3700, 1, PriceType.LimitPrice, Side.Buy, Offset.Open)