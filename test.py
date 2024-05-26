import tkinter as tk
from tkinter import ttk, simpledialog

class RealTimeCalculationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Calculation with Treeview")

        self.tree = ttk.Treeview(root, columns=('Value',), show='headings')
        self.tree.heading('Value', text='Value')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 初期値を設定
        initial_values = [10, 20, 30, 40, 50]
        for value in initial_values:
            self.tree.insert('', tk.END, values=(value,))

        self.tree.bind('<Double-1>', self.on_double_click)
        
        # 合計ラベル
        self.sum_label = tk.Label(root, text="Sum: 0")
        self.sum_label.pack()

        # 初期合計を計算
        self.update_sum()

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)
        if column == '#1':  # 第1列（Value列）にのみ対応
            self.edit_value(item)

    def edit_value(self, item):
        old_value = self.tree.item(item, 'values')[0]
        new_value = simpledialog.askfloat("Input", "Enter new value:", initialvalue=old_value)
        if new_value is not None:
            self.tree.item(item, values=(new_value,))
            self.update_sum()

    def update_sum(self):
        total = 0
        for child in self.tree.get_children():
            total += float(self.tree.item(child, 'values')[0])
        self.sum_label.config(text=f"Sum: {total}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimeCalculationApp(root)
    root.mainloop()
