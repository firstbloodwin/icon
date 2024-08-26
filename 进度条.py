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

test()


import time
import json
from typing import Dict, Any
import traceback

import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiomysql

app = FastAPI()


class ResponseModel(BaseModel):
    success: bool
    result: list = []
    msg: str = ""


# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
DB_CONFIG = {
    'host': '10.91.21.210',
    'port': 3306,
    'user': 'bdat',
    'password': 'testpass',
    'db': 'BigDataTool',
    'minsize': 10,
    'maxsize': 20,
    'charset': 'utf8mb4',
    'autocommit': True,
    'pool_recycle': 7200,
}

# 数据库连接池
db_pool = None


@app.on_event("startup")
async def startup_event():
    global db_pool
    db_pool = await aiomysql.create_pool(**DB_CONFIG)


@app.on_event("shutdown")
async def shutdown_event():
    global db_pool
    if db_pool is not None:
        await db_pool.close()


def send_msg_to_espace(content):
    url = 'http://aresocean.huawei.com/ocean/api/auth/message'
    data = {
        # 发起方账号,示例：hwx123456 ,不填默认公共账号
        "fromUserAccount": '',
        # 接受方账号，多人逗号隔开（一条消息的接收人最多为200人，超过会失败）,示例:d00123456,x00123456
        "toUserAccount": 'lwx1297912',
        # 跳转URL,如看板地址
        "jumpUrl": '',
        # 消息内容（纯文本，不支持html、超链接、附件）, 属性长度：2000，超过将截取不显示
        "content": content,
        # 消息标题，长度：100字符，客户端显示：超过两行打点显示
        "title": "大数据后台运行异常",
        # 事件类型1通知类，2订阅类,固定填1
        "type": "1"
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Content-Type': 'application/json'}
    requests.post(url, json=data, headers=headers, verify=False)


# 检查IP是否在trace白名单中
async def check_trace_ip(ip: str):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute("SELECT COUNT(1) FROM permission WHERE category = 'trace' AND ip = %s",
                                  (ip,))
                result = await cur.fetchone()
                return result[0] > 0
            except Exception as es:
                send_msg_to_espace(traceback.format_exc())
                return False


# 检查IP是否在bdat白名单中
async def check_bdat_ip(ip: str):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute("SELECT COUNT(1) FROM permission WHERE category = 'bdat' AND ip = %s",
                                  (ip,))
                result = await cur.fetchone()
                return result[0] > 0
            except Exception as es:
                send_msg_to_espace(traceback.format_exc())
                return False


# 日志记录
async def log_record(username: str, process_type: str, local_ip: str, headers: str, data: str, results: str, msg: str,
                     time_str: str):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                value = (username, process_type, local_ip, headers, data, results, msg, time_str)
                await cur.execute(
                    "INSERT INTO log (username,process_type,local_ip,header,data,results,msg,timestamp_str) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    value)
            except Exception as es:
                send_msg_to_espace(traceback.format_exc())


# trace权限校验接口
@app.get("/trace/ip")
async def check_permission(request: Request):
    ip = request.headers.get('X-Real-IP', 'error')
    time_str = request.headers.get('timestamp', 'error')
    check_sign = False
    header_str = '{}'
    res = '0'
    try:
        header_str = json.dumps(dict(request.headers))
        check_sign = await check_trace_ip(ip)
        res = '1' if check_sign is True else '0'
        await log_record('ip', 'trace', ip, header_str, '{}', res, '', time_str)
    except Exception as es:
        send_msg_to_espace(traceback.format_exc())
        await log_record('ip', 'trace', ip, header_str, '{}', res, traceback.format_exc(), time_str)
    finally:
        return ResponseModel(success=check_sign, result=[], msg=ip)


# bdat权限校验接口
@app.get("/bdat/ip")
async def check_permission(request: Request):
    ip = request.headers.get('X-Real-IP', 'error')
    time_str = request.headers.get('timestamp', 'error')
    check_sign = False
    header_str = '{}'
    res = '0'
    try:
        header_str = json.dumps(dict(request.headers))
        check_sign = await check_bdat_ip(ip)
        res = '1' if check_sign is True else '0'
        await log_record('ip', 'bdat', ip, header_str, '{}', res, '', time_str)
    except Exception as es:
        send_msg_to_espace(traceback.format_exc())
        await log_record('ip', 'bdat', ip, header_str, '{}', res, traceback.format_exc(), time_str)
    finally:
        return ResponseModel(success=check_sign, result=[], msg=ip)


@app.post("/bdat/dataAPI")
async def proxy_query(request: Request, data: Dict[str, Any]):
    try:
        api_url = 'http://aresocean-query.rnd.huawei.com:9666/interface/queryAPI'
        process_type = data.get('process', 'Error')
        username = data.get('user', 'Error')
        time_str = request.headers.get('timestamp', 'error')
        ip = ''
        header_str = '{}'
        data_str = json.dumps(data)
        res = '0'
        msg_str = ''
        try:
            ip = request.headers.get('X-Real-IP', 'error')
            header_str = json.dumps(dict(request.headers))
            new_header = {k: v for k, v in request.headers.items() if k not in ['X-Real-IP', 'X-Forwarded-For']}
            response = requests.post(url=api_url, headers=new_header, json=data)
            result = response.json()
            if result is None:
                await log_record(username, process_type, ip, header_str, data_str, res, "None data!!", time_str)
                return ResponseModel(success=False, result=[], msg="Empty data!!")
            msg_str = result['msg']
            if response.status_code == 200:
                res = '1'
                await log_record(username, process_type, ip, header_str, data_str, res, msg_str, time_str)
                return result
            else:
                res = '0'
                await log_record(username, process_type, ip, header_str, data_str, res, response.text, time_str)
                return ResponseModel(success=False, result=[], msg='Query Error')
        except Exception as es:
            res = '0'
            send_msg_to_espace(traceback.format_exc())
            await log_record(username, process_type, ip, header_str, data_str, res, traceback.format_exc(), time_str)
            return ResponseModel(success=False, result=[], msg='Query Error')
    except Exception as es:
        return ResponseModel(success=False, result=[], msg='Query Error')

config


import multiprocessing
import os

# 设置守护进程
daemon = False
# 监听内网端口
bind = '0.0.0.0:20240'

graceful_timeout = 100
timeout = 400

# 设置进程文件目录
pidfile = './gunicorn.pid'
chdir = './'  # 工作目录
# 工作模式
worker_class = 'uvicorn.workers.UvicornWorker'
# 并行工作进程数 核心数*2+1个
workers = multiprocessing.cpu_count() + 1
# 指定每个工作者的线程数
threads = 3
# 设置最大并发量
worker_connections = 2000
loglevel = 'debug'  # 错误日志的日志级别
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
# 设置访问日志和错误信息日志路径
log_dir = "./log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

accesslog = "./log/gunicorn_access.log"
errorlog = "./log/gunicorn_error.log"





 query_resp = await response.json()
  File "C:\Users\lWX1297912\AppData\Roaming\Python\Python38\site-packages\aiohttp\client_reqrep.py", line 1194, in json
    raise ContentTypeError(
aiohttp.client_exceptions.ContentTypeError: 0, message='Attempt to decode JSON with unexpected mimetype: text/html', url=URL('http://10.91.21.210:8341/bdat/dataAPI')
