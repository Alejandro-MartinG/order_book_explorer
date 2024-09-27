import unittest
import pandas as pd
from unittest.mock import Mock, patch
from src.services.stats_service import StatsService

class TestStatsService(unittest.TestCase):
    def setUp(self):
        self.stats_service = StatsService()
        self.stats_service.db = Mock()

    def test_get_order_book_stats_empty_df(self):
        df = pd.DataFrame()
        result = self.stats_service._get_order_book_stats(df)
        self.assertEqual(result, {})

    def test_get_order_book_stats_missing_columns(self):
        df = pd.DataFrame({'px': [1, 2, 3]})
        result = self.stats_service._get_order_book_stats(df)
        self.assertIn('error', result)
        self.assertEqual(result['error'], "Missing required columns in DataFrame")

    def test_get_order_book_stats_valid_data(self):
        df = pd.DataFrame({
            'px': [100, 200, 300],
            'qty': [1, 2, 3],
            'num': [1, 2, 3]
        })
        result = self.stats_service._get_order_book_stats(df)
        self.assertIn('average_value', result)
        self.assertIn('greater_value', result)
        self.assertIn('lesser_value', result)
        self.assertIn('total_qty', result)
        self.assertIn('total_px', result)

    @patch('src.services.stats_service.StatsService._get_order_book_stats')
    def test_get_bids_stats(self, mock_get_order_book_stats):
        mock_df = pd.DataFrame()
        self.stats_service.db.get_bids.return_value = mock_df
        mock_get_order_book_stats.return_value = {'test': 'data'}
        
        result = self.stats_service.get_bids_stats('BTC-USD')
        
        self.stats_service.db.get_bids.assert_called_once_with(symbol='BTC-USD')
        mock_get_order_book_stats.assert_called_once_with(mock_df)
        self.assertEqual(result, {'test': 'data'})

    def test_get_general_stats(self):
        mock_df = pd.DataFrame({
            'symbol': ['BTC-USD', 'BTC-USD', 'ETH-USD', 'ETH-USD'],
            'type': ['bid', 'ask', 'bid', 'ask'],
            'px': [100, 110, 200, 210],
            'qty': [1, 1, 2, 2]
        })
        self.stats_service.db.get_all_data.return_value = mock_df
        
        result = self.stats_service.get_general_stats()
        
        self.assertIn('BTC-USD', result)
        self.assertIn('ETH-USD', result)
        self.assertEqual(result['BTC-USD']['bids']['count'], 1)
        self.assertEqual(result['BTC-USD']['asks']['count'], 1)
        self.assertEqual(result['ETH-USD']['bids']['count'], 1)
        self.assertEqual(result['ETH-USD']['asks']['count'], 1)

if __name__ == '__main__':
    unittest.main()
