# Trade

### DataType
该文件夹存储的是交易数据的数据类型定义，包括交易数据的结构体定义、以及用于测试kungfu的枚举类；
* `enums.py`：枚举类定义,用于测试，实际运行的代码不会涉及到该类
  1. 如果在kungfu存在同种enum，那么此类与kungfu的enum类保持一致，或者减少类中属性；
  2. kungfu的enums类设置在CPP文件中，如需调整相关的enmus，还需要修改cpp文件再编译。因此，后续所使用的相关enums设置在此易于优化；
  3. 此文件中的enums类，不会在kungfu中使用，只会在自定义函数和类中使用，区别kungfu相关的enums方式目前设置为：import DataType.enums as HJEnums；
* `orderType.py`:此文件为定义订单类型的文件，目前包括了Target, RealTarget, TradeOrder三个类

### Collector
* `TargetPosition.py`:涉及到统计周期内的下单指令，进行汇总计算、下单、结合已成交订单的回调信息计算结果的类；
  1. 用于读取某个时间段所有策略的目标持仓数据，然后将该持仓数据整合，传入到kungfu的on_quote，进行下单；
  2. kungfu交易函数执行完毕后，获取对应的一成交后的交易数据，结合该数据计算策略相关属性；

### Recorder
* `client.py`:数据库的基类，用于定义数据库的基本操作，可连接不同数据库类型； 目前已连接的数据库类型:clickhouse
* `Daily.py`:用于获取每日更新的全局参数，目前已包括：每日所有期货合于。可设计为单类。
* `getTick.py`:获取tick数据，并存入clickhouse中。
* `TPstrategy.py`:结合TargetPosition.py使用，计算并返回某个周期内的所有已成交订单；


