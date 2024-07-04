from dataclasses import dataclass, field
from typing import Optional
from kungfu.wingchun.constants import Side, Offset, Direction, PriceType, OrderStatus, Exchange
from enum import Enum
'''
此文件为定义订单类型的文件，目前包括了Target, RealTarget, TradeOrder三个类
'''

@dataclass
class Target:
    strategy_id: str                                                    #策略id
    instrument_id: str                                                  #合约代码
    exchange:Exchange                                                   #合约对应的交易所
    side: Side                                                          #买卖方向
    offset: Offset                                                      #开平方向
    nominal: float                                                      #名义价值,包括了multiply
    limit_price: float                                                  #交易限价
    weights:Optional[float] = field(default=None, init=False)           #权重
    order_id:Optional[int] = field(default=None, init=False)            #订单id(与实际成交相匹配的订单，存在一个订单匹配多个策略Target类的情况)
    real_nominal:Optional[float]= field(default=None, init=False)       #实际买入的金额


    def __eq__(self, other):
        if self.instrument_id == other.instrument_id and self.side == other.side and self.offset == other.offset:
            return True
        return False


@dataclass
class RealTarget:
    instrument_id: str                                                  # 合约代码
    exchange: Exchange                                                  # 合约对应的交易所
    side: Side                                                          # 买卖方向
    offset: Offset                                                      # 开平方向
    nominal: float                                                      # 名义价值,预期买入的金额
    limit_price: float                                                  # 交易限价
    order_id: Optional[int]= field(default=None, init=False)            # 订单id
    real_nominal:Optional[float]= field(default=None, init=False)       # 实际买入的金额
    tax:Optional[float]= field(default=None, init=False)                # 税费
    commission:Optional[float]= field(default=None, init=False)         # 手续费


    def __eq__(self, other):
        if self.instrument_id == other.instrument_id and self.side == other.side and self.offset == other.offset:
            return True
        return False


@dataclass
class TradeOrder:
    trade_id: int                    #成交id
    parent_order_id: int             #母订单id
    external_order_id: str           #柜台订单id
    external_trade_id: str           #柜台成交编号id
    order_id: int                    #kungfu订单id
    trade_time: int                  #成交时间(功夫时间)
    trading_day: int                 #交易日
    # restore_time: int                #恢复时间(用于重启交易账户td后回复交易数据的时间戳)
    instrument_id: str               #合约ID
    exchange_id: str                 #交易所ID
    side: Side                       #买卖方向
    offset: Offset                   #开平方向
    price: float                     #成交价格
    volume: float                    #成交数量
    tax:float                        #税费
    commission:float                 #手续费

class OrderProcess(Enum):
    '''
    订单处理流程
    '''
    collect = 0
    Order = 1
    Trade = 2

class OrderFollow(Enum):
    Drop = 0                        # 在规定时间内未成交单直接撤单，后续不再对该单进行下单
    Keep = 1                        # 直到所有单成交才进行下一轮订单分发
    Append = 2                      # 本轮未成交的单，撤单后继续跟单

