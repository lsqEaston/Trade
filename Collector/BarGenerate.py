
import kungfu.yijinjing.time as kft
from DataType.barType import Bar


class BarGenerator:
    """
    合成Bar
    """
    def __init__(self, context, on_bar:callable, time_interval:int=60):
        """
        :param on_bar:callable:bar合成后的回调函数
        :param time_interval: 时间间隔(秒)，默认合成1分钟bar
        """
        self.ctx = context
        self.on_bar = on_bar
        self.time_interval_nano = time_interval * kft.NANO_PER_SECOND

        # 交易所给到的quote中volume, turnover是累计数据, 相减得到当前bar
        self.start_quote = None

        self.bar: Bar = None

        self.last_quote = None

    def generate_new_bar(self, quote)->None:
        """
        生成新的Bar
        :param quote:交易所更新的quote
        """
        self.bar = Bar(
            instrument_id=quote.instrument_id,
            exchange_id=quote.exchange_id,
            start_time=quote.data_time - quote.data_time % self.time_interval_nano,
            end_time=quote.data_time - quote.data_time % self.time_interval_nano + self.time_interval_nano,
            open=quote.last_price,
            high=quote.last_price,
            low=quote.last_price,
            close=quote.last_price,
            volume=quote.volume - self.last_quote.volume if self.last_quote else 0,
            turnover=quote.turnover - self.last_quote.turnover if self.last_quote else 0,
            open_interest=quote.open_interest
            # 暂留接口
            # ask_price=quote.ask_price,
            # bid_price=quote.bid_price,
            # ask_volume=quote.ask_volume,
            # bid_volume=quote.bid_volume
        )
        self.start_quote = self.last_quote if self.last_quote else quote

    def update_quote(self, quote)->None:
        """
        update Bar value
        :param quote:交易所更新的quote
        """
        if not self.bar:
            # 生成bar
            self.generate_new_bar(quote)
        elif quote.data_time > self.bar.end_time:
            # 生成bar 回调
            self.on_bar(self.ctx, self.bar)
            # 运行回调函数后生成新的bar
            self.generate_new_bar(quote)
        else:
            # 更新bar OHLC volume turnover open_interest
            self.bar.high = max(self.bar.high, quote.last_price)
            self.bar.low = min(self.bar.low, quote.last_price)
            self.bar.close = quote.last_price
            # 累积值(当前值-bar开始值)
            self.bar.volume = quote.volume - self.start_quote.volume
            self.bar.turnover = quote.turnover - self.start_quote.turnover

            self.bar.open_interest = quote.open_interest

        self.last_quote = quote

