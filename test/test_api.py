import unittest
from unittest.mock import patch
from src.api import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    @patch('src.services.stats_service.StatsService.get_bids_stats')
    def test_get_bids_stats(self, mock_get_bids_stats):
        mock_get_bids_stats.return_value = {'test': 'data'}
        response = self.app.get('/bids/stats?symbol=BTC-USD')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'test': 'data'})

    @patch('src.services.stats_service.StatsService.get_asks_stats')
    def test_get_asks_stats(self, mock_get_asks_stats):
        mock_get_asks_stats.return_value = {'test': 'data'}
        response = self.app.get('/asks/stats?symbol=BTC-USD')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'test': 'data'})

    @patch('src.services.stats_service.StatsService.get_general_stats')
    def test_get_general_stats(self, mock_get_general_stats):
        mock_get_general_stats.return_value = {'BTC-USD': {'test': 'data'}}
        response = self.app.get('/general/stats')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'BTC-USD': {'test': 'data'}})

    def test_missing_symbol(self):
        response = self.app.get('/bids/stats')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Symbol parameter is required"})

if __name__ == '__main__':
    unittest.main()
