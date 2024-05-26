# 株価と配当率のスクレイピング
from bs4 import BeautifulSoup
import requests
import urllib.robotparser

# 各URLの設定
robot_url = "https://minkabu.jp/robots.txt"
basic_url = "https://minkabu.jp/stock/"

item = []

# クローリング可能かチェック
def check_crawling(url):
    ur = urllib.robotparser.RobotFileParser()
    ur.set_url(robot_url)
    ur.read()
    result = ur.can_fetch("*", url)
    return result

# スクレイピングの実行
def scraping(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    stock_name = soup.find('p', class_='md_stockBoard_stockName').text # 証券名

    # 配当金抽出
    dividend_percent = soup.find_all(
        "td", attrs={"class": "ly_vamd_inner ly_colsize_9_fix fwb tar wsnw"}
    )
    # 株価抽出
    current_price = soup.find("div", attrs={"class": "stock_price"}).text

    # 抽出した文字の整形
    current_price = current_price.replace(",", "")
    current_price = current_price.replace("\n", "")
    current_price = current_price.replace(" ", "")
    current_price = current_price.replace("円", "")

    # 株価と配当金をリストに追加
    if current_price == "---":
        current_price = 0
    else:
        current_price = float(current_price)
    
    if dividend_percent[4].string == "---": # 沖縄セルラーの値が取れなかったため対応
        dividend_percent = 0.01
    else:
        dividend_percent = dividend_percent[4].string.replace("%", "")
        
    return stock_name, dividend_percent, current_price

# 全ての証券番号の情報を抜き出す
def search_stock(ticker_symbol):
    # 指定した証券番号のURLを作成
    url = basic_url + ticker_symbol
    if check_crawling(url):
        # 株価、配当金を返す
        return scraping(url) # dividend_percent, current_price