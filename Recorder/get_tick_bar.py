
from pathlib import Path
import sys
sys.path.append(Path(__file__).absolute().parent.parent)
sys.path.append('/export/extraData/pythonFiles/')
from clickhouse_driver import Client
from kungfu.wingchun.constants import *
import kungfu.yijinjing.time as kft

from Daily import DAILY
from client import ClickHouseDB, UpdateLang
from Collector.BarGenerate import BarGenerator
from DataType.barType import Bar

# 柜台
source = "sim"
# 账户
# account = "225203"
account = "test"
# 目标行情源
md_source = "sim"

# 建立clickhouse连接
DB = ClickHouseDB(host='localhost', port='9000', database='TEST', user='default', password='123456')
client = DB.connect()

# 初始化用于存储合成bar的字典，key为instrument_id, value为BarGenerator对象
bar_generators : dict[str, BarGenerator]= {}
# 每TIME_INTERVAL合成一个bar
TIME_INTERVAL = 60


def on_bar(context, bar:Bar):
    # 合成bar数据录入
    DB.insert_data(client,"ctp_bar", "* EXCEPT(writed_time)", UpdateLang.update_bar(bar))

# 启动前回调，添加交易账户，订阅行情，策略初始化计算等
def pre_start(context):
    context.log.info("preparing strategy")
    context.log.info(f"{DAILY.SYMBOLS}")
    for exc, symbol in DAILY.SYMBOLS.items():
        context.subscribe(source, symbol, eval("Exchange.{}".format(exc)))
    context.log.info("subscribe success")


    # context.subscribe(source, ["600000", "600004", "600006", "600007"], Exchange.SSE)
    context.add_account(source, account)

    global bar_generators
    for exc, instrument_ids in DAILY.SYMBOLS.items():
        for instrument_id in instrument_ids:
            bar_generators[instrument_id] = BarGenerator(context, on_bar, time_interval=TIME_INTERVAL)
            context.add_timer(context.now()- context.now() % (TIME_INTERVAL * kft.NANO_PER_SECOND) + TIME_INTERVAL * kft.NANO_PER_SECOND,
                              lambda context, e: context.add_time_interval(TIME_INTERVAL * kft.NANO_PER_SECOND,
                              lambda context, e: bar_generators[instrument_id].update_time_interval()))

# 快照数据回调
def on_quote(context, quote, location, dest):
    # tick数据录入
    DB.insert_data(client,"ctp_quote", "* EXCEPT(writed_time, total_bid_volume, total_ask_volume, total_trade_num)",UpdateLang.update_quote(quote))

    # 合成bar数据录入
    global bar_generators
    # if quote.instrument_id not in bar_generators:
    #     bar_generators[quote.instrument_id] = BarGenerator(context, on_bar, time_interval=TIME_INTERVAL)
    bar_generators[quote.instrument_id].update_quote(quote)


# 订单回报
def on_order(context, order, location, dest):
    pass


# 成交回报
def on_trade(context, trade, location, dest):
    pass

# 策略进程退出前方法
def post_stop(context):
    context.log.info(f"quit tickSaver")
    pass

