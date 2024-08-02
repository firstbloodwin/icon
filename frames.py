import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext


class TraceFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.trace_num = 0
        self.productname_enrty = tk.Entry(self)
        self.productversion_enrty = tk.Entry(self)
        self.start_date_entry = tk.Entry(self)
        self.end_date_entry = tk.Entry(self)
        self.sn_model_var = tk.IntVar(value=0)
        self.input_model = ttk.Radiobutton(self,
                                           text="直接输入",
                                           variable=self.sn_model_var,
                                           value=0,
                                           command=self.sn_model_change)
        self.file_model = ttk.Radiobutton(self,
                                          text="文件导入",
                                          variable=self.sn_model_var,
                                          value=1,
                                          command=self.sn_model_change)
        self.download_model = tk.IntVar(value=0)
        self.all_file = ttk.Radiobutton(self,
                                        text="全部下载",
                                        variable=self.download_model,
                                        value=0,
                                        command=self.download_model_change)
        self.sub_file = ttk.Radiobutton(self,
                                        text="部分下载",
                                        variable=self.download_model,
                                        value=1,
                                        command=self.download_model_change)
        self.btn_start_search = tk.Button(self, text="开始查询")
        self.sn_entry = tk.Entry(self)
        self.file_path_entry = tk.Entry(self)
        self.btn_select_file = tk.Button(self,
                                         text="选择文件",
                                         command=self.select_file)
        self.select_sheet = ttk.Combobox(self)
        self.down_load_num_entry = tk.Entry(self)
        self.btn_start_down = tk.Button(self,
                                        text="开始下载",
                                        command=self.select_file)
        self.info_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.create_page()
        self.sn_model_change()
        self.download_model_change()

    def create_page(self):
        tk.Label(self, text="产品名称").grid(row=0,
                                         column=0,
                                         columnspan=4,
                                         pady=20,
                                         sticky='ew')
        tk.Label(self, text="产品").grid(row=1, column=0, pady=10, sticky='w')
        self.productname_enrty.grid(row=1,
                                    column=1,
                                    pady=10,
                                    columnspan=3,
                                    sticky='ew')
        tk.Label(self, text="版本").grid(row=2, column=0, pady=10, sticky='w')
        self.productversion_enrty.grid(row=2,
                                       column=1,
                                       pady=10,
                                       columnspan=3,
                                       sticky='ew')
        tk.Label(self, text="开始日期").grid(row=3, column=0, pady=10, sticky='w')
        self.start_date_entry.grid(row=3, column=1, pady=10, sticky='ew')
        tk.Label(self, text="结束日期").grid(row=3, column=2, pady=10, sticky='w')
        self.end_date_entry.grid(row=3, column=3, pady=10, sticky='ew')
        tk.Label(self, text="型号").grid(row=4, column=0, pady=10, sticky='w')
        self.input_model.grid(row=4, column=1, pady=10, sticky='w')
        self.file_model.grid(row=4, column=2, pady=10, sticky='w')
        self.btn_start_search.grid(row=4, column=3, pady=10, sticky='e')
        self.sn_entry.grid(row=5, column=0, pady=10, sticky='ew', columnspan=4)
        self.btn_select_file.grid(row=6, column=0, pady=10, sticky='w')
        self.file_path_entry.grid(row=6,
                                  column=1,
                                  pady=10,
                                  sticky='ew',
                                  columnspan=2)
        self.select_sheet.grid(row=6, column=3, pady=10, sticky='e')
        tk.Label(self, text="下载模式").grid(row=7, column=0, pady=10, sticky='w')
        self.all_file.grid(row=7, column=1, pady=10, sticky='w')
        self.sub_file.grid(row=7, column=2, pady=10, sticky='w')
        tk.Label(self, text="请输入下载数量").grid(row=8,
                                            column=0,
                                            pady=10,
                                            sticky='w',
                                            columnspan=2)
        self.down_load_num_entry.grid(row=8, column=1, pady=10, sticky='w')
        self.btn_start_down.grid(row=8, column=2, pady=10, sticky='w')
        self.info_text.grid(row=9,
                            column=0,
                            columnspan=4,
                            pady=10,
                            sticky='ew')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        self.file_path_entry.config(state='normal')
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)
        self.file_path_entry.config(state='readonly')

    def sn_model_change(self):
        if self.sn_model_var.get() == 0:
            self.sn_entry.config(state='normal')
            self.file_path_entry.config(state='disabled')
            self.btn_select_file.config(state='disabled')
            self.select_sheet.config(state='disabled')
        else:
            self.sn_entry.config(state='disabled')
            self.file_path_entry.config(state='normal')
            self.btn_select_file.config(state='normal')
            self.select_sheet.config(state='normal')

    def download_model_change(self):
        if self.download_model.get() == 0:
            self.down_load_num_entry.config(state='normal')
            self.down_load_num_entry.delete(0, tk.END)
            self.down_load_num_entry.config(state='disabled')
        else:
            self.down_load_num_entry.config(state='normal')


class LoginFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.username_entry = tk.Entry(self)
        self.password_entry = tk.Entry(self, show='*')
        self.btn_login = tk.Button(self, text="登录")
        self.create_page()

    def create_page(self):
        tk.Label(self, text="用户名").grid(row=0, column=0, pady=10, sticky='w')
        tk.Label(self, text="密码").grid(row=1, column=0, pady=10, sticky='w')
        self.username_entry.grid(row=0, column=1, pady=10, sticky='ew')
        self.password_entry.grid(row=1, column=1, pady=10, sticky='ew')
        self.btn_login.grid(row=2, column=1, pady=10, sticky='e')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
