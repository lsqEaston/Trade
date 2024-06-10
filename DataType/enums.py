'''
构建以下enum类有以下标准，目标：用于测试，实际运行的代码不会涉及到该类：
1.如果在kungfu存在同种enum，那么此类与kungfu的enum类保持一致，或者减少类中属性；
2.kungfu的enums类设置在CPP文件中，如需调整相关的enmus，还需要修改cpp文件再编译。因此，后续所使用的相关enums设置在此易于优化；
3.此文件中的enums类，不会在kungfu中使用，只会在自定义函数和类中使用，区别kungfu相关的enums方式目前设置为：import DataType.enums as HJEnums；
'''
from enum import Enum

class Exchange(Enum):
    BSE = "BSE"             # 北交所
    SSE = "SSE"             # 上交所
    SZE = "SZE"             # 深交所
    SHFE = "SHFE"           # 上期所
    DCE = "DCE"             # 大商所
    CZCE = "CZCE"           # 郑商所
    CFFEX = "CFFEX"         # 中金所
    INE = "INE"             # 上海能源中心
    GFEX = "GFEX"           # 广期所


class Offset(Enum):
    Open=0               #开仓
    Close=1              #平仓
    CloseToday=2         #平今
    CloseYesterday=3     #平昨

class Side(Enum):
    Buy=0                #买
    Sell=1               #卖

class LedgerCategory(Enum):
    Account=0            #账户投资组合数据
    Strategy=1           #策略投资组合数据

class Direction(Enum):
    Long=0               #多
    Short=1              #空


class PriceType(Enum):
    Limit=0                   #限价，通用
    Any=1                     #市价，通用。对于股票上海为最优5档剩余撤销，深圳为即时成交剩余撤销
    FakBest5=2                #上海最优五档即时成交剩余撤销,不需要报价
    ForwardBest=3             #仅深圳本方最优价格申报，不需要报价
    ReverseBest=4             #上海最优五档即时成交剩余转限价，深圳对手方最优价格申报，不需要报价
    Fak=5                     #股票（仅深圳）即时成交剩余撤销，不需要报价；期货即时成交剩余撤销，需要报价
    Fok=6                     #股票（仅深圳）即时全额成交否则撤销，不需要报价；期货全部成交或撤销，需要报价
    EnhancedLimit=7           #增强限价盘-港股
    AtAuctionLimit=8          #增强限价盘-港股
    AtAuction=9               #港股竞价盘，期货（竞价盘的价格就是开始价格）
