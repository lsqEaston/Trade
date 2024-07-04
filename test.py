from dataclasses import dataclass, field
from typing import Optional
from multiprocessing import Queue
from kungfu.wingchun.constants import Side, Offset, Direction, PriceType, OrderStatus, Exchange
import pandas as pd
from DataType.orderType import Target, TradeOrder, RealTarget, OrderProcess
from Collector.TargetPosition import TargetPosHander
import random
'''
用于测试，可忽略
'''
@dataclass
class Quote:
    data_time:int
    instrument_id:str
    exchange_id:str
    last_price:float


tarPosHander = TargetPosHander()

# from kungfu.wingchun.constants import

target1 = Target('strat1', 'rb1906', Exchange.CFFEX, Side.Buy.value, Offset.Open.value, 10000.12, 200)
quote1 = Quote(1717481305500000000, 'rb1906', Exchange.CFFEX, 200.12)

target2 = Target('strat1', 'rb1906', Exchange.CFFEX, Side.Buy.value, Offset.Open.value, 20000.12, 201.12)
quote2 = Quote(1717481305500000012, 'rb1906', Exchange.CFFEX, 202.12)

target3 = Target('strat2', 'rb1906', Exchange.CFFEX, Side.Buy.value, Offset.Open.value, 30000.12,202.12)
quote3 = Quote(1717481305500000055, 'rb1906', Exchange.CFFEX, 200.42)

target4 = Target('strat2', 'rb1906', Exchange.CFFEX, Side.Buy.value, Offset.Open.value, 40000.12, 200.52)
quote4 = Quote(1717481305500000089, 'rb1906', Exchange.CFFEX, 203.42)

target5 = Target('strat1', 'rb1906', Exchange.CFFEX, Side.Sell.value, Offset.Close.value, 50000.12, 205.12)
quote5 = Quote(1717481305500000089, 'rb1906', Exchange.CFFEX, 204.42)

target6 = Target('strat1', 'rb1907', Exchange.CFFEX, Side.Sell.value, Offset.Close.value, 50000.12, 522.41)
quote6 = Quote(1717481305500000121, 'rb1907', Exchange.CFFEX, 523.42)

target7 = Target('strat1', 'rb1907', Exchange.CFFEX, Side.Sell.value, Offset.Close.value, 50000.12, 522.50)
quote7 = Quote(1717481305500000232, 'rb1907', Exchange.CFFEX, 525.42)

target8 = Target('strat1', 'rb1907', Exchange.CFFEX, Side.Sell.value, Offset.CloseToday.value, 50000.12,527.12)
quote8 = Quote(1717481305500000532, 'rb1907', Exchange.CFFEX, 528.42)

class Log:
    @staticmethod
    def info(msg):
        print(msg)
class Context:
    def __init__(self):
        self.log = Log()
    def insert_order(self, instrument_id, exchange, source, account, last_price, volumn, priceType, side, offset):
        print('insert order sucessful:{}'.format( instrument_id, exchange, source, account, last_price, volumn, priceType, side, offset))
        return random.randint(1,200)


context = Context()

# 添加策略任务
tarPosHander.add_target(target1)
tarPosHander.add_target(target2)
tarPosHander.add_target(target3)
tarPosHander.add_target(target4)
tarPosHander.add_target(target5)
tarPosHander.add_target(target6)
tarPosHander.add_target(target7)
tarPosHander.add_target(target8)



# targets.append(target1)
# targets.append(target2)
# targets.append(target3)
# targets.append(target4)
# targets.append(target5)
# targets.append(target6)
# targets.append(target7)
# targets.append(target8)
#
# targets = pd.DataFrame(targets)

# 回调计算所有下单至功夫的订单
# total_nominal, strt_nominal = tarPosHander.calc_order_nominal()
# tarPosHander.calc_weights(total_nominal, strt_nominal)
# tarPosHander.add_total_orders(total_nominal)# 初始化总订单
# tarPosHander.process.next()
# tarPosHander.update_order_timer(context, tarPosHander.pre_targets, PriceType.Any, 'ctp', '225203')
tarPosHander.callback_timer_init(context, PriceType.Any, 'ctp','225203')




# # 行情回调交易时开启
# # 前往on_quote下单:模拟 --> post_targets
# for quote_ in [quote1, quote2, quote3, quote4, quote5, quote6, quote7, quote8]:
#     # tarPosHander.order_by_quote(context, quote_, 'ctp', '225203')
#     tarPosHander.callback_quote(context, quote_, 'ctp', '225203')

order_id_list = list(tarPosHander.post_targets.keys())

# 通过功夫的on_trade获取已成交的信息
# 制造trade信息
tradeInfoList = []
for order_id, real_target in tarPosHander.post_targets.items():
    tradeOrder = TradeOrder(order_id, 1, '1',
                            '1',
                            order_id, 0, 0, real_target.instrument_id, real_target.exchange,
                            real_target.side, real_target.offset, random.randint(200,220), random.randint(5,15), random.randint(1,20),
                            random.randint(1,10))
    tradeInfoList.append(tradeOrder)

# on_trade中调用以下函数
for trade in tradeInfoList:
    # tarPosHander.update_by_trade(trade)
    tarPosHander.callback_trade(context, trade)


# output
print(pd.DataFrame(tarPosHander.res['target']))
# ------------------------------------output(Begin)------------------------------------
'''
    strategy_id instrument_id exchange       side             offset    nominal  \
0      strat1        rb1906    CFFEX   Side.Buy        Offset.Open   30000.24   
1      strat2        rb1906    CFFEX   Side.Buy        Offset.Open   70000.24   
2      strat1        rb1906    CFFEX  Side.Sell       Offset.Close   50000.12   
3      strat1        rb1907    CFFEX  Side.Sell       Offset.Close  100000.24   
4      strat1        rb1907    CFFEX  Side.Sell  Offset.CloseToday   50000.12   
    weights  order_id  real_nominal  
0  0.300001       129    436.801398  
1  0.699999       129   1019.198602  
2  1.000000        58   2856.000000  
3  1.000000       144   1704.000000  
4  1.000000        66   1881.000000  
'''
# ------------------------------------output(end)------------------------------------

print(pd.DataFrame(tarPosHander.res['realTarget']))
# ------------------------------------output(Begin)------------------------------------
'''
    instrument_id exchange       side             offset    nominal  order_id  \
0        rb1906    CFFEX   Side.Buy        Offset.Open  100000.48       129   
1        rb1906    CFFEX  Side.Sell       Offset.Close   50000.12        58   
2        rb1907    CFFEX  Side.Sell       Offset.Close  100000.24       144   
3        rb1907    CFFEX  Side.Sell  Offset.CloseToday   50000.12        66   
   real_nominal  tax  commission  
0          1456   15           1  
1          2856    7           3  
2          1704    3          10  
3          1881   14           6  
'''
# ------------------------------------output(end)------------------------------------












# ------------------------------------output------------------------------------

'''
    def update_order(self, context, quote, order_targets:dict, source:str, account:str)->None:
        if len(order_targets) > 0:
            if quote.instrument_id in order_targets.keys():
                for realTarget in order_targets[quote.instrument_id]:
                    vol = realTarget.nominal // quote.last_price
                    order_id = context.insert_order(quote.instrument_id, realTarget.exchange, source, account,
                                                    quote.last_price, vol, PriceType.Limit,
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
                            context.log.info(f"下单成功，下单信息为：{realTarget}")

                    # next(self.process) # self.process = OrderProcess.Trade
                # 下单完毕后，删除pre_targets中的相关合约信息
                del order_targets[quote.instrument_id]
        # return order_targets
        
        
            # 下单-->前往on_quote()下单-->下单完毕后会更新post_targets列表中的realTarget类
    def order_by_quote(self,context, quote, source, account):
        # 分组聚合后执行下单交易
        if self.process.value == OrderProcess.Order or self.process.value == OrderProcess.Trade:
            # self.pre_targets = self.update_order(context, quote, self.pre_targets, source, account)
            # self.follow_targets = self.update_order(context, quote, self.follow_targets, source, account)

            if len(self.pre_targets) > 0:
                if quote.instrument_id in self.pre_targets.keys():
                    realTargetList = self.pre_targets[quote.instrument_id]
                    for realTarget in realTargetList:
                        vol = realTarget.nominal/quote.last_price
                        order_id = context.insert_order(quote.instrument_id, realTarget.exchange, source, account,
                                                        quote.last_price, vol, PriceType.Limit,
                                                        realTarget.side, realTarget.offset)
                        if order_id > 0:
                            # 第一个下单完毕后，可以开始接受trade回调信息
                            if self.process.value == OrderProcess.Order:
                                self.process.next()

                            realTarget.order_id = order_id
                            self.post_targets[realTarget.order_id] = realTarget

                            # 下单成功后，如果是Append或者Drop，需要设置延时取消订单
                            if self.order_follow == OrderFollow.Drop or self.order_follow == OrderFollow.Append:
                                context.add_timer(context.now() + self.__DELAY, lambda context,event: self.cancel_order(context, order_id))

                            if self.__DEBUG:
                                context.log.info(f"下单成功，下单信息为：{realTarget}")


                        # next(self.process) # self.process = OrderProcess.Trade
                    # 下单完毕后，删除pre_targets中的相关合约信息
                    del self.pre_targets[quote.instrument_id]

        if self.process.value == OrderProcess.Order:
            if self.order_follow == OrderFollow.Append:
                if len(self.follow_targets)>0:
                    if quote.instrument_id in self.follow_targets.keys():
                        realTargetList = self.follow_targets[quote.instrument_id]
                        for realTarget in realTargetList:
                            vol = realTarget.nominal / quote.last_price
                            order_id = context.insert_order(quote.instrument_id, realTarget.exchange, source, account,
                                                            quote.last_price, vol, PriceType.Limit,
                                                            realTarget.side, realTarget.offset)
                            if order_id > 0:
                                # 第一个下单完毕后，可以开始接受trade回调信息
                                if self.process.value == OrderProcess.Order:
                                    self.process.next()

                                realTarget.order_id = order_id
                                self.post_targets[realTarget.order_id] = realTarget

                                # 下单成功后，如果是Append或者Drop，需要设置延时取消订单
                                context.add_timer(context.now() + self.__DELAY,
                                                      lambda context, event: self.cancel_order(context, order_id))

                                if self.__DEBUG:
                                    context.log.info(f"补单成功，下单信息为：{realTarget}")
                        del self.follow_targets[quote.instrument_id]
                        
    # 策略启动时调用
    def callback_init(self, context):
        if self.process.value == OrderProcess.collect:
            context.log.info("initialize all strategy orders")
            if not self.targets.empty():
                total_nominal, strt_nominal = self.calc_order_nominal() # 计算策略和账户合约nominal
                self.calc_weights(total_nominal, strt_nominal) # 计算权重
                self.add_total_orders(total_nominal)  # 初始化总订单
                self.process.next()
                if self.__DEBUG:
                    context.log.info("orders send to Kungfu")
                    # context.log.info(self.pre_targets)
                return
        if self.process.value == OrderProcess.Order:
            context.log.info("ordering......from Kungfu to Exchange")
        if self.process.value == OrderProcess.Trade:
            context.log.info("waiting......get deal callback from Exchange")
            
# 行情回调时调用
    def callback_quote(self, context, quote, source, account):
        self.order_by_quote(context, quote, source, account)

        
'''