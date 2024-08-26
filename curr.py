# pip install --upgrade fastapi

import time
import json
from typing import Dict, Any
import traceback

import requests
import asyncio
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
    'host': '127.0.0.1',
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
db_pool: aiomysql.Pool = None


async def database_pool_health_check():
    while True:
        if db_pool is not None:
            async with db_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
        await asyncio.sleep(1800)


@app.on_event("startup")
async def startup_event():
    global db_pool
    db_pool = await aiomysql.create_pool(**DB_CONFIG)
    asyncio.create_task(database_pool_health_check())


@app.on_event("shutdown")
async def shutdown_event():
    global db_pool
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()


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
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Content-Type': 'application/json'
    }
    requests.post(url, json=data, headers=headers, verify=False)


# 检查IP是否在trace白名单中
async def check_trace_ip(ip: str):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(
                    "SELECT COUNT(1) FROM permission WHERE category = 'trace' AND ip = %s",
                    (ip, ))
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
                await cur.execute(
                    "SELECT COUNT(1) FROM permission WHERE category = 'bdat' AND ip = %s",
                    (ip, ))
                result = await cur.fetchone()
                return result[0] > 0
            except Exception as es:
                send_msg_to_espace(traceback.format_exc())
                return False


# 日志记录
async def log_record(username: str, process_type: str, local_ip: str,
                     headers: str, data: str, results: str, msg: str,
                     time_str: str):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                value = (username, process_type, local_ip, headers, data,
                         results, msg, time_str)
                await cur.execute(
                    "INSERT INTO log (username,process_type,local_ip,header,data,results,msg,timestamp_str) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    value)
            except Exception as es:
                send_msg_to_espace(traceback.format_exc())


# trace权限校验接口
@app.get("/trace/ip")
async def check_trace_permission(request: Request):
    ip = request.headers.get('X-Real-IP', 'error')
    time_str = request.headers.get('timestamp', 'error')
    check_sign = False
    header_str = '{}'
    res = '0'
    try:
        header_str = json.dumps(dict(request.headers))
        check_sign = await check_trace_ip(ip)
        res = '1' if check_sign is True else '0'
        await log_record('ip', 'trace', ip, header_str, '{}', res, '',
                         time_str)
    except Exception as es:
        send_msg_to_espace(traceback.format_exc())
        await log_record('ip', 'trace', ip, header_str, '{}', res,
                         traceback.format_exc(), time_str)
    finally:
        return ResponseModel(success=check_sign, result=[], msg=ip)


# bdat权限校验接口
@app.get("/bdat/ip")
async def check_bdat_permission(request: Request):
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
        await log_record('ip', 'bdat', ip, header_str, '{}', res,
                         traceback.format_exc(), time_str)
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
            # token
            curr_header = {'Accept': 'application/json'}
            # data
            curr_data = {}
            response = requests.post(url=api_url,
                                     headers=curr_header,
                                     json=curr_data)
            try:
                result = response.json()
            except ValueError:
                # JSON解析失败处理
                error_info = {'JSONerror': response.text}
                await log_record(username, process_type, ip, header_str,
                                 data_str, res, "None data!!", time_str)
                return ResponseModel(success=False,
                                     result=[],
                                     msg="Empty data!!")
            if result is None:
                await log_record(username, process_type, ip, header_str,
                                 data_str, res, "None data!!", time_str)
                return ResponseModel(success=False,
                                     result=[],
                                     msg="Empty data!!")
            msg_str = result.get('msg', 'Msg None data!!')
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '').lower()
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                    except ValueError:
                        error_info = {'JSONerror': response.text}
                    except json.JSONDecodeError:
                        error_info = {'JSONerror': response.text}
                    finally:
                        await log_record(username, process_type, ip,
                                         header_str, data_str, res,
                                         "None data!!", time_str)
                        return ResponseModel(success=False,
                                             result=[],
                                             msg="Empty data!!")
                else:
                    error_info = {
                        'JSONerror': response.text,
                        'Content-Type': content_type
                    }

                res = '1'
                await log_record(username, process_type, ip, header_str,
                                 data_str, res, msg_str, time_str)
                return result
            else:
                res = '0'
                await log_record(username, process_type, ip, header_str,
                                 data_str, res, response.text, time_str)
                return ResponseModel(success=False,
                                     result=[],
                                     msg='Query Error')
        except Exception as es:
            res = '0'
            send_msg_to_espace(traceback.format_exc())
            await log_record(username, process_type, ip, header_str, data_str,
                             res, traceback.format_exc(), time_str)
            return ResponseModel(success=False, result=[], msg='Query Error')
    except Exception as es:
        return ResponseModel(success=False, result=[], msg='Query Error')
