import unittest
import pandas as pd
from unittest.mock import Mock, patch
from src.db.db import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.database = Database()

    @patch('sqlite3.connect')
    def test_connect(self, mock_connect):
        self.database.connect()
        mock_connect.assert_called_once_with(self.database.database_name)

    @patch('sqlite3.connect')
    def test_close(self, mock_connect):
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        self.database.connect()
        self.database.close()
        mock_connection.close.assert_called_once()

    def test_create_tables(self):
        with patch('sqlite3.connect') as mock_connect:
            mock_cursor = Mock()
            mock_connect.return_value.cursor.return_value = mock_cursor
            self.database.create_tables()
            self.assertEqual(mock_cursor.execute.call_count, 2)
            mock_connect.return_value.commit.assert_called_once()

    def test_create_table_sql_sentence(self):
        result = self.database.create_table_sql_sentence('test_table')
        self.assertIn('CREATE TABLE IF NOT EXISTS test_table', result)

    @patch('pandas.DataFrame.to_sql')
    @patch('sqlite3.connect')
    def test_save_into_table(self, mock_connect, mock_to_sql):
        df = pd.DataFrame()
        self.database.save_into_table('test_table', df)
        mock_to_sql.assert_called_once_with('test_table', mock_connect.return_value, if_exists='append', index=False)

    @patch('sqlite3.connect')
    def test_get_data_from_db(self, mock_connect):
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, 'BTC-USD', 100, 1, 1)]
        mock_cursor.description = [('id',), ('symbol',), ('px',), ('qty',), ('num',)]
        mock_connect.return_value.cursor.return_value = mock_cursor

        result = self.database.get_data_from_db('SELECT * FROM test_table')

        mock_cursor.execute.assert_called_once_with('SELECT * FROM test_table')
        self.assertIsInstance(result, pd.DataFrame)
        expected_df = pd.DataFrame([(1, 'BTC-USD', 100, 1, 1)], 
                                   columns=['id', 'symbol', 'px', 'qty', 'num'])
        pd.testing.assert_frame_equal(result, expected_df)

    def test_get_bids(self):
        with patch.object(Database, 'get_data_from_db') as mock_get_data:
            self.database.get_bids('BTC-USD')
            mock_get_data.assert_called_once_with(sql_sentence="SELECT * FROM bids WHERE symbol = 'BTC-USD'")

    def test_get_asks(self):
        with patch.object(Database, 'get_data_from_db') as mock_get_data:
            self.database.get_asks('BTC-USD')
            mock_get_data.assert_called_once_with(sql_sentence="SELECT * FROM asks WHERE symbol = 'BTC-USD'")

    def test_get_all_data(self):
        with patch.object(Database, 'get_data_from_db') as mock_get_data:
            self.database.get_all_data()
            mock_get_data.assert_called_once_with(sql_sentence="SELECT *, 'bid' as type FROM bids UNION ALL SELECT *, 'ask' as type FROM asks")

if __name__ == '__main__':
    unittest.main()
