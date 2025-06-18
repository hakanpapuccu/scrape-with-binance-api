import requests
from flask import Flask, render_template, jsonify, abort
from datetime import datetime

app = Flask(__name__)

def datetimeformat(value):
    return datetime.fromtimestamp(value/1000).strftime('%Y-%m-%d %H:%M')

app.jinja_env.filters['datetimeformat'] = datetimeformat

def get_top_100_coins():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    data = response.json()
    # Sadece USDT paritelerini al, hacme göre sırala
    usdt_pairs = [item for item in data if item["symbol"].endswith("USDT") and not item["symbol"].endswith("BUSD")]
    top_100 = sorted(usdt_pairs, key=lambda x: float(x["quoteVolume"]), reverse=True)[:100]
    result = []
    for item in top_100:
        result.append({
            "symbol": item["symbol"],
            "price": item["lastPrice"],
            "priceChangePercent": item["priceChangePercent"],
            "volume": item["volume"],
            "openPrice": item["openPrice"],
            "highPrice": item["highPrice"],
            "lowPrice": item["lowPrice"],
            "bidPrice": item["bidPrice"],
            "askPrice": item["askPrice"],
            "weightedAvgPrice": item["weightedAvgPrice"],
            "count": item["count"]
        })
    return result

def get_coin_detail(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

def get_coin_klines(symbol, interval="1h", limit=24):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    return response.json()

@app.route("/")
def index():
    coins_data = get_top_100_coins()
    return render_template("index.html", coins=coins_data)

@app.route("/api/top20")
def api_top20():
    return jsonify(get_top_100_coins())

@app.route("/coin/<symbol>")
def coin_detail(symbol):
    detail = get_coin_detail(symbol)
    if not detail:
        abort(404)
    klines = get_coin_klines(symbol)
    return render_template("coin_detail.html", coin=detail, klines=klines)

if __name__ == "__main__":
    app.run(debug=True) 