
import kungfu.yijinjing.time as kft
from DataType.barType import Bar
from typing import Union, List, Type
import pandas as pd
class CrossSection:
    def __init__(self, window:Union[int,list[int]], bar_property=list[str]):
        self.window = window
        self.last_bars: dict[str, Bar]  = {}
        self.bar_property = bar_property
        self.last_update=0
        self.update_timestamp=0
        for p in self.bar_property:
            setattr(self, p, pd.DataFrame())
        for w in self.window:
            setattr(self, f"y_{w}", pd.DataFrame())

    def update_bar(self, bar:Bar, method='ignore'):
        """
        :param bar:每个固定周期获取的bar
        :param method: ignore表示：如果当前更新的bar与之前的bar一致，
        即没有新的行情、挂单、成交，此bar不会作为新数据加入至因子计算中；
        否则,无论当前更新的bar与之前的bar是否一致，都会作为新数据加入至因子计算中
        :return: None
        """
        if method=='ignore':
            if bar.volume == 0:
                return
        self.last_bars[bar.instrument_id] = bar
        self.update_timestamp = bar.end_time

    def generate(self):
        if self.update_timestamp == self.last_update:
            return

        for p in self.bar_property:
            d = {
                f"{instrument_id}.{bar.exchange_id}": getattr(bar, p) for instrument_id, bar in self.last_bars.items()
            }# col:insturment_ids, value:p
            d["datetime"] = kft.to_datetime(self.update_timestamp)
            df = getattr(self, p) # 第一次 空dataframe
            df = pd.concat([df, pd.DataFrame([d]).set_index("datetime")])# add one row
            # 超过size，取最新size行
            if len(df) > self.window:
                df = df.iloc[-self.window:]
            setattr(self, p, df)# update p: index:time, col:insturment_ids, value:p
        self.last_update = self.update_timestamp

    def factor_impbalance(self):
        return ((self.bid_volume[0] - self.ask_volume[0]) / (self.bid_volume[0] + self.ask_volume[0])).iloc[-1,:].dropna()




# class FactorEvaluation:
#     """
#     盘后评估，回测实现
#     """





