import pandas as pd
import numpy as np
from src.db.db import Database

class StatsService:
    def __init__(self) -> None:
        self.db = Database()

    def _get_order_book_stats(self, df: pd.DataFrame):
        if df.empty:
            return {}

        required_columns = ["qty", "px", "num"]
        if not all(column in df.columns for column in required_columns):
            return {
                "error": "Missing required columns in DataFrame"
            }

        if df["qty"].empty or df["px"].empty or not pd.api.types.is_numeric_dtype(df["qty"]) or not pd.api.types.is_numeric_dtype(df["px"]):
            return {
                "error": "Invalid data in qty or px columns"
            }

        try:
            df["value"] = df["px"] * df["qty"]

            average_value = df["value"].mean()
            greater_value = df.loc[df["value"].idxmax()]
            lesser_value = df.loc[df["value"].idxmin()]
            total_qty = df["qty"].sum()
            total_px = df["value"].sum()

            return {
                "average_value": float(average_value),
                "greater_value": {
                    "px": float(greater_value["px"]),
                    "qty": float(greater_value["qty"]),
                    "num": int(greater_value["num"]),
                    "value": float(greater_value["value"])
                },
                "lesser_value": {
                    "px": float(lesser_value["px"]),
                    "qty": float(lesser_value["qty"]),
                    "num": int(lesser_value["num"]),
                    "value": float(lesser_value["value"])
                },
                "total_qty": float(total_qty),
                "total_px": float(total_px)
            }
        except Exception as e:
            return {
                "error": f"An unexpected error occurred: {str(e)}"
            }

    def get_bids_stats(self, symbol: str):
        bids_df = self.db.get_bids(symbol=symbol)
        return self._get_order_book_stats(bids_df)

    def get_asks_stats(self, symbol):
        asks_df = self.db.get_asks(symbol=symbol)
        return self._get_order_book_stats(asks_df)

    def get_general_stats(self):
        df = self.db.get_all_data()
        symbols = df["symbol"].unique()
        result = {}
        for symbol in symbols:
            symbol_df = df[df["symbol"] == symbol]
            bids = symbol_df[symbol_df["type"] == "bid"]
            asks = symbol_df[symbol_df["type"] == "ask"]
            result[symbol] = {
                "bids": {
                    "count": len(bids),
                    "qty": float(bids["qty"].sum()),
                    "value": float((bids["px"] * bids["qty"]).sum())
                },
                "asks": {
                    "count": len(asks),
                    "qty": float(asks["qty"].sum()),
                    "value": float((asks["px"] * asks["qty"]).sum())
                }
            }
        return result
