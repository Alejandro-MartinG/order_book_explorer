import requests
import pandas as pd
from src.db.db import Database
import sys

def get_symbol_data(symbol: str):
    BASE_URL = 'https://api.blockchain.com/v3/exchange'
    url = f"{BASE_URL}/l3/{symbol}"
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data

def transform_data(data, symbol):
    bids = pd.DataFrame(data['bids'])
    bids['symbol'] = symbol
    asks = pd.DataFrame(data['asks'])
    asks['symbol'] = symbol

    columns_map = {'px': 'px', 'qty': 'qty', 'num': 'num'}
    bids.rename(columns=columns_map, inplace=True)
    asks.rename(columns=columns_map, inplace=True)

    return bids, asks

def run(symbol):
    if not symbol:
        raise ValueError("No symbol provided.")

    try:
        data = get_symbol_data(symbol)
        bids, asks = transform_data(data, symbol)

        db = Database()
        db.save_into_table('bids', bids)
        db.save_into_table('asks', asks)

        print(f"Order book data saved for symbol {symbol}")
        print("Bids:")
        print(bids)
        print("\nAsks:")
        print(asks)
    except requests.RequestException as e:
        print(f"Error fetching data for symbol {symbol}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        run(symbol.upper())
    else:
        print("Please provide a symbol as a command-line argument.")
        print("Example: python src/data_loader.py near-usdt")
