from abc import ABC, abstractmethod
from clickhouse_driver import errors
'''
数据库的基类，用于定义数据库的基本操作，可连接不同数据库类型；
目前已连接的数据库类型:clickhouse
'''
class DataBase(ABC):
    '''
    所有数据库的基类,根据实际需求增加方法
    '''
    @abstractmethod
    def connect(self, *args):
        pass

    @abstractmethod
    def create_table(self, *args):
        pass

    @abstractmethod
    def insert_data(self, *args):
        pass


class ClickHouseDB(DataBase):
    """
    使用clickhouse相关的api构建database
    """
    def __init__(self, host:str, port:str, database:str, user:str, password:str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        # self.client = self.connect()


    def connect(self):
        from clickhouse_driver import Client
        client = Client(host=self.host, port=self.port, database=self.database, user=self.user,
                        password=self.password)

        return self.__valid_connect(client)

    def create_table(self, client, table_name:str, sql_lang:str):
        client.execute(f"CREATE TABLE {table_name} {sql_lang}")

    def insert_data(self, client, table_name:str, columns:str, sql_lang:str):
        client.execute(f"INSERT INTO {table_name} ({columns}) VALUES {sql_lang}")

    def insert_one_col(self, client, table_name: str, column: str, sql_lang: str):
        client.execute(f"INSERT INTO {table_name} ({column}) VALUES ({sql_lang})")


    def __valid_connect(self, client):
        try:
            client.execute('show tables')
            return client
        except errors.SocketTimeoutError:
            raise ValueError('Invalid host')
        except BrokenPipeError:
            raise ValueError('Invalid databse, please input correct database name to connect')
        except errors.ServerException:
            raise ValueError('Invalid user or password')
        except errors.NetworkError:
            raise ValueError('Invalid port')

    @staticmethod
    def exec(client, sql_lang:str):
        return client.execute(sql_lang)




class UpdateLang:
    '''
    纯静态函数类：用于根据kungfu的数据字段构建clickhouse的sql语句
    '''
    @staticmethod
    def update_quote(quote):
        return f"""{quote.data_time, quote.instrument_id, quote.exchange_id, quote.pre_close_price,
        quote.pre_settlement_price, quote.last_price, quote.volume, quote.turnover,
        quote.pre_open_interest, quote.open_interest, quote.open_price, quote.high_price,
        quote.low_price, quote.upper_limit_price, quote.lower_limit_price, quote.close_price,
        quote.settlement_price, quote.bid_price, quote.ask_price, quote.bid_volume, quote.ask_volume}"""

    @staticmethod
    def update_bar(bar):
        return f"""{bar.instrument_id, bar.exchange_id, bar.start_time, bar.end_time,
        bar.open, bar.high, bar.low, bar.close, bar.open_interest, bar.volume, bar.turnover,
        bar.ask_price, bar.bid_price, bar.ask_volume, bar.bid_volume}"""
    @staticmethod
    def update_pos(pos):
        pass









'''
from dataclasses import dataclass, field
@dataclass
class Quote:
    data_time:int = 1717481305500000000
    instrument_id:str = 'test'
    exchange_id:str = 'test'
    pre_close_price:float = 0
    pre_settlement_price:float = 0
    last_price:float = 0
    volume:int = 0
    turnover:float = 0
    pre_open_interest:int = 0
    open_interest:int = 0
    open_price:float = 0
    high_price:float = 0
    low_price:float = 0
    upper_limit_price:float = 0
    lower_limit_price:float = 0
    close_price:float = 0
    settlement_price:float = 0
    bid_price:list[float] = field(default_factory=lambda:[0,0,0,0,0])
    ask_price:list[float] = field(default_factory=lambda:[0,0,0,0,0])
    bid_volume:list[int] = field(default_factory=lambda:[0,0,0,0,0])
    ask_volume:list[int] = field(default_factory=lambda:[0,0,0,0,0])
# print(UpdateLang.update_quote(Quote()))

# DB = ClickHouseDB(host='localhost',port='9000',database='default',user='default',password='123456')
# DB.connect()
# DB.insert_data('ctp_quote',"* EXCEPT(writed_time)",UpdateLang.update_quote('ctp_quote',Quote()))

# DB.insert_data("ctp_quote", "* EXCEPT(writed_time, total_bid_volume, total_ask_volume, total_trade_num)",UpdateLang.update_quote(Quote()))

'''












