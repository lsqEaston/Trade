
from pathlib import Path
import sys

import pandas as pd

sys.path.append(Path(__file__).absolute().parent.parent)
sys.path.append('/export/extraData/pythonFiles/')
from DataType.orderType import Target, TradeOrder, RealTarget, OrderProcess
from Collector.TargetPosition import TargetPosHander
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

TIME_INTERVAL=60


# 初始化TargetPosition类
targetPosHander = TargetPosHander()

# 建立clickhouse连接
# DB = ClickHouseDB(host='localhost', port='9000', database='default', user='default', password='123456')
# client = DB.connect()


# def test(context):
#     context.log.info("add timer inteval function running!!!")

# 启动前回调，添加交易账户，订阅行情，策略初始化计算等
def pre_start(context):
    context.log.info("preparing strategy")
    context.log.info(f"{DAILY.SYMBOLS}")
    for exc, symbols in DAILY.SYMBOLS.items():
        context.subscribe(source, symbols, eval("Exchange.{}".format(exc)))
    context.log.info("subscribe success")
    context.add_account(source, account)




    # 增加时间间隔回调函数
    context.add_timer(context.now() - context.now() % (TIME_INTERVAL * kft.NANO_PER_SECOND) + TIME_INTERVAL * kft.NANO_PER_SECOND,
                      lambda ctx, e: context.add_time_interval(TIME_INTERVAL * kft.NANO_PER_SECOND,
                      lambda ctx, e: targetPosHander.callback_timer_init(context, PriceType.Any, source, account)))



# 快照数据回调
def on_quote(context, quote, location, dest):
    # example：用于发射假的交易信号
    # global targetPosHander
    if targetPosHander.targets.qsize() < 30:
        if quote.last_price %2 ==0:
            target = Target('strtegy_1', quote.instrument_id, quote.exchange_id ,Side.Buy, Offset.Open, 100000, quote.last_price)
        else:
            target = Target('strtegy_2', quote.instrument_id, quote.exchange_id, Side.Buy, Offset.Open, 100000, quote.last_price)
        targetPosHander.add_target(target)

    # 分组聚合后执行下单交易(行情回调下单才开启)
    # targetPosHander.callback_quote(context, quote, source, account)

# 订单回报
def on_order(context, order, location, dest):
    targetPosHander.update_by_order(context, order)


# 成交回报
def on_trade(context, trade, location, dest):
    targetPosHander.callback_trade(context, trade)


# 策略进程退出前方法
def post_stop(context):
    import pandas
    _date = kft.strftime(kft.today_start(), '%Y%m%d')
    pd.DataFrame(targetPosHander.res['target']).to_csv(f'./{_date}_target.csv')
    pd.DataFrame(targetPosHander.res['realTarget']).to_csv(f'./{_date}_realTarget.csv')
    context.log.info(f"output path:{Path(__file__).absolute().parent}")
    context.log.info(f"Server quit")

