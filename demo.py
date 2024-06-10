
from clickhouse_driver import Client
from kungfu.wingchun.constants import *
import kungfu.yijinjing.time as kft
'''
用于测试，可忽略
'''
# 柜台
source = "sim"
# 账户
account = "simTest"
# 目标行情源
md_source = "sim"
# 建立clickhouse连接
client = Client(host='172.16.6.139', port= '9000', database='default', user='default', password='')

def update_quote(client,quote):
    sql_insert = f"INSERT INTO ctp_quote (* EXCEPT(writed_time)) VALUES {quote.data_time, quote.instrument_id, quote.exchange_id, quote.pre_close_price,quote.pre_settlement_price, quote.last_price, quote.volume, quote.turnover, quote.pre_open_interest,quote.open_interest, quote.open_price, quote.high_price, quote.low_price, quote.upper_limit_price,quote.lower_limit_price, quote.close_price, quote.settlement_price, quote.total_bid_volume,quote.total_ask_volume, quote.total_trade_num, quote.bid_price, quote.ask_price, quote.bid_volume, quote.ask_volume}"
    client.execute(sql_insert)
    return None

# quote行情数据字段
# data_quote = ['data_time', 'instrument_id', 'exchange_id', 'pre_close_price', 'pre_settlement_price', 'last_price',
#               'volume', 'turnover', 'pre_open_interest', 'open_interest', 'open_price', 'high_price', 'low_price',
#               'upper_limit_price', 'lower_limit_price', 'close_price', 'settlement_price', 'total_bid_volume',
#               'total_ask_volume', 'bid_price', 'ask_price', 'bid_volume', 'ask_volume']


# 获取持仓
def get_position(instrument_id, book):
    long_position = None
    for pos in book.long_positions.values():
        if instrument_id == pos.instrument_id:
            long_position = pos
    return long_position


# 启动前回调，添加交易账户，订阅行情，策略初始化计算等
def pre_start(context):
    context.log.info("preparing strategy")

    # context.subscribe(source, ["600000", "600004", "600006", "600007"], Exchange.SSE)
    # context.subscribe(source, ["000001", "000004", "000005", "000006"], Exchange.SZE)
    context.add_account(source, account)
    context.subscribe_all(md_source)


# 快照数据回调
def on_quote(context, quote, location, dest):
    # context.log.info(f"{quote=}")
    update_quote(client, quote)

    # context.log.info(f"insert data: {quote}")
    # context.log.info(f"data_time: {quote.data_time}")
    # context.log.info(f"instrument id: {quote.instrument_id}")
    # context.log.info(f"bid_price: {quote.bid_price}")
    # context.log.info(f"ask_volume: {quote.ask_volume}")


# 订单回报
def on_order(context, order, location, dest):
    pass


# 成交回报
def on_trade(context, trade, location, dest):
    context.log.info(f"{trade=}")
    pass


# 策略进程退出前方法
def post_stop(context):
    book = context.book
    # context.log.info("trades: \n", list(book.trades.items()))
    context.log.info(f"{book.long_positions=}")
    pass

# sql = 'SELECT * FROM ctp_quote'
# res = client.execute(sql)
# print(res)


