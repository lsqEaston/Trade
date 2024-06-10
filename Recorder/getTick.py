
from pathlib import Path
import sys
sys.path.append(Path(__file__).absolute().parent.parent)

from clickhouse_driver import Client
from kungfu.wingchun.constants import *
import kungfu.yijinjing.time as kft

from Daily import DAILY
from client import ClickHouseDB, UpdateLang

# 柜台
source = "ctp"
# 账户
account = "225203"
# account = "test"
# 目标行情源
md_source = "ctp"

# 建立clickhouse连接
DB = ClickHouseDB(host='localhost', port='9000', database='default', user='default', password='123456')
client = DB.connect()

# 启动前回调，添加交易账户，订阅行情，策略初始化计算等
def pre_start(context):
    context.log.info("preparing strategy")
    context.log.info(f"{DAILY.SYMBOLS}")
    for exc, symbols in DAILY.SYMBOLS.items():
        context.subscribe(source, symbols, eval("Exchange.{}".format(exc)))
    context.log.info("subscribe success")


    # context.subscribe(source, ["600000", "600004", "600006", "600007"], Exchange.SSE)
    context.add_account(source, account)


# 快照数据回调
def on_quote(context, quote, location, dest):
    # context.log.info(f"{quote=}")
    # update_quote(client, quote)
    # context.log.info(UpdateLang.update_quote(quote))
    DB.insert_data("ctp_quote", "* EXCEPT(writed_time, total_bid_volume, total_ask_volume, total_trade_num)",UpdateLang.update_quote(quote))

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

