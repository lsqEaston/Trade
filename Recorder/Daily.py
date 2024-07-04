from dataclasses import dataclass, field
import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
# print(Path(__file__).absolute().parent.parent / 'DataType')
import DataType.enums as HJEnums

'''
用于获取每日更新的参数，可设计为单类
'''

def getContracts(*args:HJEnums.Exchange)->dict:
    '''
    :param args:交易所枚举类
    :return: 交易所对应的合约代码
    '''
    symbols = {}
    def BytushareAPI(symbols):
        import tushare as ts
        pro = ts.pro_api('0d9223de9a848ebf6f2e268039b1762919bfbcb1826df44246220d4c')
        today = datetime.datetime.now().strftime("%Y%m%d")


        for exc in [*args]:
            day_df = pro.fut_basic(**{"exchange": exc.value,"fut_type": "","ts_code": "","fut_code": "","limit": "","offset": ""},
                                   fields=["ts_code", "symbol","delist_date"])

            day_df.set_index('symbol', inplace=True)
            symbols[exc.value] = day_df[day_df.delist_date >= today].index.tolist()
        return symbols
    return BytushareAPI(symbols)

def getAllContracts() -> dict:
    '''
    :return:获取所有期货合约代码
    '''
    return getContracts(HJEnums.Exchange.CFFEX, HJEnums.Exchange.CZCE, HJEnums.Exchange.DCE, HJEnums.Exchange.SHFE, HJEnums.Exchange.INE, HJEnums.Exchange.GFEX)


@dataclass
class Daily:
    """
    单例:每日需要更新的固定参数类
    """
    TODAY: str = field(default_factory=lambda: datetime.datetime.now().strftime('%Y%m%d'), init=False)
    SYMBOLS: dict = field(default_factory=getAllContracts, init=False)

DAILY = Daily()

