'''
结合kungfu的add_time_interval()时间间隔回调使用
1.用于读取某个时间段所有策略的目标持仓数据，然后将该持仓数据整合，传入到kungfu的交易函数中；
2.kungfu交易函数执行完毕后，获取对应的交易数据，将该交易数据返回；
'''

from multiprocessing import Queue
from kungfu.wingchun.constants import Side, Offset, Direction, PriceType, OrderStatus, Exchange
import pandas as pd


'''
1.on_quote计算策略交易信号，交易信号按每分钟汇总，汇总到TargetPosHander中；
2.每分钟调用add_time_interval()，将TargetPosHander中的交易信号传入到kungfu的交易函数中；
3.交易函数执行完毕后，获取对应的交易数据，将该交易数据返回；
'''

class TargetPosHander:
    def __init__(self):
        # 多个策略传入
        self.targets = Queue()
        self.resTargets=[]
        # 通过kungfu下单前的targets
        self.pre_targets = {}
        # 下单完毕后的targets
        self.post_targets = {}
        # 收到成交信息后的结果保存
        self.res= {'target':[], 'realTarget':[]}
    def add_target(self, target: Target):
        self.targets.put(target)

    # 在每分钟末计算的时候，targets所有内容都要清空
    def get_targets(self):
        lst = []
        while not self.targets.empty():
            lst.append(self.targets.get())
        return lst


    #根据Target中的策略id，合约代码，买卖方向，开平方向，计算多个Target的nominal
    def calc_order_nominal(self):
        targets = self.get_targets()
        targets = pd.DataFrame(targets)
        # 计算每个策略的nominal总和
        strt_nominal = targets.groupby(['strategy_id', 'instrument_id', 'exchange', 'side', 'offset'])['nominal'].sum()
        # 计算每个合约的nominal总和
        total_nominal = targets.groupby(['instrument_id', 'exchange', 'side', 'offset'])['nominal'].sum()
        return total_nominal, strt_nominal


    # 计算所有周期内所有策略的权重
    def calc_weights(self, total_nominal, strt_nominal):
        # 计算权重
        weights=strt_nominal/total_nominal
        weights_df = pd.concat([strt_nominal,weights.rename('weights')], axis=1)

        for index, df in weights_df.iterrows():
            orderTarget = Target(index[0], index[1], index[2], Side(index[3]), Offset(index[4]), df.nominal)
            orderTarget.weights = df.weights
            self.resTargets.append(orderTarget)


    # 初始化总订单
    def add_total_orders(self, total_nominal:pd.DataFrame):
        for index, nominal in total_nominal.items():
            if index[0] not in self.pre_targets.keys():
                self.pre_targets[index[0]] = []
            self.pre_targets[index[0]].append(RealTarget(index[0], index[1], Side(index[2]), Offset(index[3]), nominal))


    # 处理一分钟内未成交的订单，选择撤销或者重新发送
    def handle_unTrade(self, context, unFilledIDs: list) -> list[int]:
        cancelIDs = []
        for orderID in unFilledIDs:
            cancelID = context.cancel_order(orderID)
            cancelIDs.append(cancelID)
            context.log.warning(f'{cancelID}规定时间内未成交，进行撤单处理！')
        return cancelIDs


    # 获取已成交后的信息,根据成交前的权重和已成交的数量和价格，计算成交后的权重
    def collect_trade(self,realTarget:RealTarget):
        '''
        :param orderData:kungfu返回的已成交订单情况;
        :param targets: 周期内所有策略的汇总，将要发送给kungfu的某个订单
        :param orderIDs: kungfu下单的订单号（只包括了已成交的订单）
        :return:
        '''
        for target in self.resTargets:
            if target == realTarget:#(instrument_id, side, offset)
                target.order_id = realTarget.order_id
                target.real_nominal = target.weights * realTarget.real_nominal
                self.res['target'].append(target)


    # 下单-->前往on_quote()下单-->下单完毕后会更新post_targets列表中的realTarget类
    def order_by_quote(self,context, quote, source, account):
        # 分组聚合后执行下单交易
        if len(self.pre_targets) > 0:
            if quote.instrument_id in self.pre_targets.keys():
                realTargetList = self.pre_targets[quote.instrument_id]
                for realTarget in realTargetList:
                    vol = realTarget.nominal/quote.last_price
                    order_id = context.insert_order(quote.instrument_id, realTarget.exchange, source, account,
                                                    quote.last_price, vol, PriceType.Limit,
                                                    realTarget.side, realTarget.offset)
                    realTarget.order_id = order_id

                    self.post_targets[realTarget.order_id] = realTarget

                del self.pre_targets[quote.instrument_id]

    # on_trade返回成交回报后的信息-->更新成交后的策略信息
    def update_by_trade(self, trade):
        realTarget = self.post_targets[trade.order_id]
        realTarget.real_nominal = trade.volume * trade.price
        realTarget.commission = trade.commission
        realTarget.tax = trade.tax

        self.collect_trade(realTarget)
        self.res['realTarget'].append(realTarget)


    # 策略启动时调用
    def callback_pre(self, context, quote, exchange_id, source_id, account_id, priceType):
        # 统计按策略和合约的target nominal
        total_nominal, strt_nominal = self.calc_order_nominal()

        # 计算周期内所有策略的权重
        self.calc_weights(total_nominal, strt_nominal)

        # 对总订单初始化
        self.add_total_orders(total_nominal)



        # 未成交订单
        # unFilledIDs = self.handle_unTrade(context, orderIDs)













# kungfu 下单
# context.insert_order(instrument_id, exchange_id, source_id, account_id, limit_price, volume, priceType, side, offset)
# context.insert_order("rb1906", Exchange.SHFE, "sim", "simTest", 3700, 1, PriceType.LimitPrice, Side.Buy, Offset.Open)