import tkinter as tk
import customtkinter as ctk
import database_operations as db
import stock_price_report_generator as spg

from tkinter import ttk, messagebox, simpledialog

# グローバル変数定義
difference_sum = 0 # 差額合計金額表示用
All_count_value = 0 # 全合計金額

# データを追加するボタンのコールバック
def add_stock():
    ticker_symbol = ticker_symbol_entry.get() # 証券コード取得
    if ticker_symbol:
        try:
            stock_name, dividend_percent, current_price = spg.search_stock(ticker_symbol) # 株価と配当金取得
            db.insert_data(ticker_symbol, stock_name, dividend_percent, current_price) # 株情報新規登録
            update_stock_list() # データリストを更新
            for entry in [ticker_symbol_entry]:
                entry.delete(0, tk.END)
        except:
            messagebox.showerror("Input Error", "Please enter valid values.")
    else:
        messagebox.showerror("Input Error", "Please fill in all fields.")

# 削除ボタンのコールバック
def on_delete_button_click():
    selected_item = stock_tree.selection()
    if selected_item:
        ticker_symbol = stock_tree.item(selected_item)['values'][1]
        db.del_data(ticker_symbol)
        update_stock_list() # データリストを更新
    else:
        messagebox.showwarning("Warning", "Please select an item to delete.")

# 更新ボタンのコールバック
def update_stock_db():
    global difference_sum

    for row in stock_tree.get_children():
        try: # 値が入っていない場合はスキップ
            ID = stock_tree.item(row)['values'][0]
            expected_shares = stock_tree.item(row)['values'][8]
            if expected_shares != None: # 入力されていなければ無視
                db.update_data(ID, expected_shares) # ID, 取得予定数
        except:
            pass
    
    difference_sum = 0 # 差額合計をリセット
    update_stock_list()

# データリストを更新する関数
def update_stock_list():
    global All_count_value
    All_count_value = 0 # 初期化

    dividend_sum = 0
    stock_data = []
    
    for row in stock_tree.get_children(): # データリストを一度リセット
        stock_tree.delete(row)
    
    for stock in db.fetch_data():
        # 配当金予想(円)を計算
        ID, ticker_symbol, stock_name, dividend_percent, current_price, acquired_shares = stock
        dividend_forecast_yen = dividend_percent / 100 * current_price * acquired_shares
        stock_data.append((ID, ticker_symbol, stock_name, dividend_percent, current_price, acquired_shares, dividend_forecast_yen))
        # 計算した結果を含むデータを挿入(iid を指定しないとstock_tree.itemのIDと一致しない)
        stock_tree.insert("", tk.END, iid=ID, values=(ID, ticker_symbol, stock_name, dividend_percent, current_price, acquired_shares, round(dividend_forecast_yen,2)))
        dividend_sum += dividend_forecast_yen
        All_count_value += current_price * acquired_shares
    
    # 配当金合計に対しての割合を表示
    for stock in stock_data:
        ID, ticker_symbol, stock_name, dividend_percent, current_price, acquired_shares, dividend_forecast_yen = stock
        dividend_ratio = round(dividend_forecast_yen / dividend_sum, 2) if dividend_sum != 0 else 0
        stock_tree.item(ID, values=(ID, ticker_symbol, stock_name, dividend_percent, current_price, acquired_shares, round(dividend_forecast_yen, 2), dividend_ratio))

    dividend_label.config(text=f"配当金合計予想: {dividend_sum:.2f}")
    total_label.config(text=f"合計金額: {dividend_sum + All_count_value:.2f}")

# ソート機能の実装
def sort_column(tree, col, reverse):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(reverse=reverse)

        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)

        tree.heading(col, command=lambda: sort_column(tree, col, not reverse)) # 再帰的に呼び出して並び替え

# ウィンドウに合わせて幅調整
def on_resize(event):
    stock_tree.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.7)


# セルをクリックしたときの処理
def on_cell_click(event):
    global difference_sum
    
    col = stock_tree.identify_column(event.x)
    if col == "#6" or col == "#9":  # acquired_shares列をクリックした場合
        selected_item = stock_tree.item(stock_tree.selection())['values']
        if selected_item == "": return # 選択されていなければ無視

        ID, ticker_symbol, stock_name, dividend_percent, current_price, acquired_shares, dividend_forecast_yen, dividend_ratio = selected_item # 選択した株情報を取得
        current_price = float(current_price)
        acquired_shares = int(acquired_shares)

        if acquired_shares == 0: # 株が1つも取得されていない場合
            current_sum_price = 0
        else:
            current_sum_price = current_price * acquired_shares # 現在所持価格
        
        input_value = simpledialog.askfloat("Numeric Input", "Enter a numeric value:")
        if input_value is not None and input_value > acquired_shares: # 入力値は所持数より大きく
            expected_shares = int(input_value)  # ユーザーが入力した新しい所持数を取得
        elif input_value is None:
            return
        else:
            messagebox.showerror("Input Error", "Please enter a value greater than acquired shares.")
            return

        predicted_sum_price = current_price * expected_shares # 入力した所持数に対しての合計価格
        difference = predicted_sum_price - current_sum_price  # 差額を計算
        stock_tree.item(ID, values=(ID, ticker_symbol, stock_name, dividend_percent, current_price, acquired_shares, dividend_forecast_yen, \
                                    dividend_ratio, expected_shares, difference)) # 取得予定株数と差額を挿入
        
        difference_sum += difference
        difference_label.config(text=f"差額合計: {difference_sum:.2f}")
        
# GUIの設定
root = ctk.CTk()
root.title("Stock Management")
root.geometry("1000x600")

# スタイルを作成
style = ttk.Style(root)
style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])  # セルの境界線を設定
style.configure("Treeview", font=('Meiryo UI', 12), foreground="black", rowheight=25, background="#B0C4DE")  # 背景色やフォント、行の高さなどを設定
style.configure("Treeview.Heading", font=('Meiryo UI', 12, 'bold'))  # 列見出しのスタイル設定
style.map("Treeview", background=[("selected", "#347083")]) # 選択時の背景を設定

# CustomTkinterの設定
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# 入力フィールド
fields = [
    ("証券コード", ticker_symbol_entry := ttk.Entry(root)),
]

for i, (label_text, entry) in enumerate(fields):
    label = tk.Label(root, text=label_text, fg="white", bg="#222222", font=('Meiryo UI', 12, 'bold'))
    label.grid(row=i, column=0)
    label.place(relx=0.05, rely=0.01)
    entry.grid(row=i, column=1)
    entry.place(relx=0.15, rely=0.01)

# ストック一覧表示(ID, ticker_symbol, stock_name, dividend_percent, current_price, acquired_shares, dividend_forecast_yen, dividend_ratio, expected_shares, difference)
stock_tree = ttk.Treeview(root, style="Treeview", columns=("ID", "株式コード", "銘柄名", "配当(%)", "現在価格", "取得数", '配当予想額(円)', '配当率/全体', '取得予定数', '差額'), show="headings")
for col in stock_tree["columns"]:
    stock_tree.heading(col, text=col, anchor="e", command=lambda c=col: sort_column(stock_tree, c, False)) # ソート機能を追加
    stock_tree.column(col, width=80, stretch=False, anchor="e")
stock_tree.grid(row=len(fields)+1, column=0, columnspan=3, padx=10, pady=10)

# 登録ボタン
add_button = ctk.CTkButton(root, text="Add Stock", command=add_stock)
add_button.grid(pady=10) # pady; 上下余白
add_button.place(relx=0.15, rely=0.06)

# 削除ボタンの作成
delete_button = ctk.CTkButton(root, text="Delete Selected", command=on_delete_button_click)
delete_button.grid(pady=10)
delete_button.place(relx=0.05, rely=0.9)

# 更新ボタンの作成
update_button = ctk.CTkButton(root, text="Update", command=update_stock_db)
update_button.grid(pady=10)
update_button.place(relx=0.8, rely=0.9)

# グリッドの行と列の配置を設定
root.grid_rowconfigure(0, weight=0)
root.grid_columnconfigure(0, weight=0)

# 合計配当金予合計ラベル
dividend_label = tk.Label(root, text="配当金合計予想: 0", bg="#222222", fg="white", font=('Meiryo UI', 12, 'bold'))
dividend_label.grid()
dividend_label.place(relx=0.5, rely=0.85)

# 差額合計ラベル
difference_label = tk.Label(root, text="差額合計: 0", bg="#222222", fg="white", font=('Meiryo UI', 12, 'bold'))
difference_label.grid()
difference_label.place(relx=0.8, rely=0.85)

# 合計金額ラベル
total_label = tk.Label(root, text="合計金額: 0", bg="#222222", fg="white", font=('Meiryo UI', 12, 'bold'))
total_label.grid()
total_label.place(relx=0.5, rely=0.9)

# アプリ起動時にデータリストを更新
update_stock_list()

# ウィンドウのリサイズイベントをバインド
root.bind('<Configure>', on_resize)
stock_tree.bind("<ButtonRelease-1>", on_cell_click)

root.mainloop()

# データベース接続の終了
db.connect_close()
