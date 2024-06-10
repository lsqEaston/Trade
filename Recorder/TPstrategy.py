
from pathlib import Path
import sys
sys.path.append(Path(__file__).absolute().parent.parent)
from Collector.TargetPosition import TargetPosHander, Target, TradeOrder, RealTarget
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

# 初始化TargetPosition类
targetPosHander = TargetPosHander()
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
    context.add_account(source, account)

    # 增加时间间隔回调函数
    context.add_timer_interval(60*10e9, targetPosHander.callback(context, ))


# 快照数据回调
def on_quote(context, quote, location, dest):
    # example：用于发射假的交易信号
    if len(targetPosHander.targets) < 30:
        if quote.last_price >200:
            target = Target('strtegy_1', quote.instrument_id, Side.Buy, Offset.Open, 10000)
            targetPosHander.add_target(target)

    # 分组聚合后执行下单交易
    targetPosHander.order_by_quote(context, quote, exchange_id, source, account)

# 订单回报
def on_order(context, order, location, dest):
    pass


# 成交回报
def on_trade(context, trade, location, dest):
    targetPosHander.update_by_trade(trade, exchange_id)


# 策略进程退出前方法
def post_stop(context):
    context.log.info(f"target position ordered quit")
    pass

