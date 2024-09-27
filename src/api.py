from flask import Flask, jsonify, request
from src.services.stats_service import StatsService

app = Flask(__name__)
stats_service = StatsService()

@app.route("/bids/stats", methods=["GET"])
def get_bids_stats():
    symbol = request.args.get('symbol', default=None, type=str)
    if symbol:
        return jsonify(stats_service.get_bids_stats(symbol.upper()))
    else:
        return jsonify({"error": "Symbol parameter is required"}), 400

@app.route("/asks/stats", methods=["GET"])
def get_asks_stats():
    symbol = request.args.get('symbol', default=None, type=str)
    if symbol:
        return jsonify(stats_service.get_asks_stats(symbol.upper()))
    else:
        return jsonify({"error": "Symbol parameter is required"}), 400

@app.route("/general/stats", methods=["GET"])
def get_general_stats():
    return jsonify(stats_service.get_general_stats())


if __name__ == "__main__":
    app.run(debug=True)
