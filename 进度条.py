# import tkinter
# from tkinter import ttk
# import time

# tk = tkinter.Tk()
# tk.geometry('250x250')

# def start():
#     one.start()

# def stop():
#     one.stop()

# one = tkinter.ttk.Progressbar(tk, length=200, orient=tkinter.HORIZONTAL)
# one.pack(pady=20)
# one['maximum'] = 100
# one['value'] = 0
# button1 = tkinter.Button(tk, text='开始', command=start)
# button1.pack()

# button2 = tkinter.Button(tk, text='停止', command=stop)
# button2.pack()
# tk.mainloop()

import tkinter as tk
from tkinter import ttk
import threading
import time


def start_progress():
    progress['value'] = 0
    max_value = 100
    progress['maximum'] = max_value
    threading.Thread(target=lambda: update_progress(max_value)).start()


def update_progress(max_value):
    try:
        for i in range(1, max_value + 1):
            time.sleep(0.1)  # 模拟程序正在运行
            progress['value'] = i
            root.update_idletasks()
        # 程序完成，设置进度条为最大值
        progress['value'] = max_value
        print("任务完成！")
    except Exception as e:
        # 程序报错，处理异常
        print(f"发生错误：{e}")
        # 可以选择将进度条设置为特定值或隐藏进度条
        progress['value'] = 0  # 或者设置为其他值来表示错误
        # 还可以显示错误消息
        error_label.config(text=f"错误：{e}", fg='red')


root = tk.Tk()
root.title("Tkinter Progressbar 示例")
root.geometry("300x180")

progress = ttk.Progressbar(root,
                           orient=tk.HORIZONTAL,
                           length=200,
                           mode="determinate")
progress.pack(pady=20)

start_button = tk.Button(root, text="开始", command=start_progress)
start_button.pack()

error_label = tk.Label(root, text="", fg='red')
error_label.pack()

root.mainloop()
