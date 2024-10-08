import sqlite3

# データベースに接続（存在しない場合は新規作成）
conn = sqlite3.connect('stocks_data.db')
cursor = conn.cursor()

# テーブルの作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker_symbol INTEGER NOT NULL UNIQUE,
    stock_name TEXT,
    dividend_percent REAL,
    current_price REAL,
    acquired_shares INTEGER
)
''') # 証券コード(stock_numbers参照), 配当, 現在価格, 発行済み株式数
conn.commit()

# データを新規挿入する関数
def insert_data(ticker_symbol, stock_name, dividend_percent, current_price):
    cursor.execute('''
    INSERT INTO stocks (ticker_symbol, stock_name, dividend_percent, current_price, acquired_shares)
    VALUES (?, ?, ?, ?, ?)
    ''', (ticker_symbol, stock_name, dividend_percent, current_price, 0))
    conn.commit()

# 最新のデータにアップデート
def current_update(ticker_symbol, dividend_percent, current_price):
    cursor.execute('UPDATE stocks SET dividend_percent = ?, current_price = ? WHERE ticker_symbol = ?', (dividend_percent, current_price, ticker_symbol))
    conn.commit()

# 取得予定数の株数に変更
def update_data(ID, expected_shares):
    cursor.execute('UPDATE stocks SET acquired_shares = ? WHERE id = ?', (expected_shares, ID))
    conn.commit()

# データを取得する関数
def fetch_data():
    cursor.execute('SELECT * FROM stocks')
    return cursor.fetchall()

def del_data(ticker_symbol):
    cursor.execute('DELETE FROM stocks WHERE ticker_symbol = ?', (ticker_symbol,))
    conn.commit()

def connect_close():
    conn.close()