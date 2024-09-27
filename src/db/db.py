import sqlite3
from pandas import DataFrame

class Database:
    def __init__(self):
        self.database_name = 'market.db'
        self.conn = None
        self.cursor = None
        self.create_tables()

    def connect(self):
        self.conn = sqlite3.connect(self.database_name)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        self.connect()
        self.cursor.execute(self.create_table_sql_sentence('bids'))
        self.cursor.execute(self.create_table_sql_sentence('asks'))
        self.conn.commit()
        self.close()

    def create_table_sql_sentence(self, table_name: str):
        return f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            px REAL,
            qty REAL,
            num INTEGER
        )
        '''

    def save_into_table(self, table_name:str, df: DataFrame):
        self.connect()
        df.to_sql(table_name, self.conn, if_exists='append', index=False)
        self.close()

    def get_data_from_db(self, sql_sentence: str):
        self.connect()
        self.cursor.execute(sql_sentence)
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        df = DataFrame(rows, columns=columns)
        self.close()
        return df

    def get_bids(self, symbol: str) -> DataFrame:
        sql_sentence = f"SELECT * FROM bids WHERE symbol = '{symbol}'"
        df = self.get_data_from_db(sql_sentence=sql_sentence)
        return df

    def get_asks(self, symbol: str) -> DataFrame:
        sql_sentence = f"SELECT * FROM asks WHERE symbol = '{symbol}'"
        df = self.get_data_from_db(sql_sentence=sql_sentence)
        return df

    def get_all_data(self) -> DataFrame:
        sql_sentence = "SELECT *, 'bid' as type FROM bids UNION ALL SELECT *, 'ask' as type FROM asks"
        df = self.get_data_from_db(sql_sentence=sql_sentence)
        return df
