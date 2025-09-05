import sqlite3
import requests
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crypto_symbol TEXT NOT NULL,
            price_usd REAL NOT NULL,
            timestamp DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Fetch price from CoinGecko API
def get_crypto_price(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get(symbol.lower(), {}).get('usd')
    return None

# Route for homepage
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# API endpoint to get price
@app.route('/get_price', methods=['POST'])
def get_price():
    symbol = request.form.get('symbol').upper()
    if symbol not in ['XRP', 'LINK', 'BTC', 'SOL', 'ETH']:
        return jsonify({'error': 'Invalid cryptocurrency symbol'}), 400
    
    price = get_crypto_price(symbol)
    if price is not None:
        # Store in database
        conn = sqlite3.connect('prices.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO prices (crypto_symbol, price_usd, timestamp) VALUES (?, ?, ?)',
                       (symbol, price, datetime.now()))
        conn.commit()
        conn.close()
        return jsonify({'symbol': symbol, 'price_usd': price})
    else:
        return jsonify({'error': 'Failed to fetch price'}), 500

if __name__ == '__main__':
    init_db()  # Initialize DB on startup
    app.run(host='0.0.0.0', port=5000, debug=True)
