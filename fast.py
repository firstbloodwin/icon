from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiomysql
import httpx
import asyncio
import json
from datetime import datetime

app = FastAPI()

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
    'user': 'your_username',
    'password': 'your_password',
    'db': 'your_database',
    'charset': 'utf8mb4',
    'autocommit': True,
}


# 数据库连接池
async def get_db_pool():
    return await aiomysql.create_pool(pool_size=10, **DB_CONFIG)


# 检查IP是否在白名单中
async def check_ip_whitelist(ip: str, db_pool):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM whitelist WHERE ip = %s",
                              (ip, ))
            result = await cur.fetchone()
            return result[0] > 0


# 接收POST数据并转发
async def forward_post_request(url: str, headers: dict, json_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=json_data)
        return response


# 日志记录
async def log_request(ip: str, headers: dict, json_data: dict, db_pool):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            log_entry = (ip, json.dumps(headers), json.dumps(json_data),
                         datetime.now())
            await cur.execute(
                "INSERT INTO logs (ip, headers, json_data, timestamp) VALUES (%s, %s, %s, %s)",
                log_entry)


# 权限校验接口
@app.post("/check-permission")
async def check_permission(request):
    ip = request.client.host
    db_pool = await get_db_pool()
    if await check_ip_whitelist(ip, db_pool):
        await log_request(ip, dict(request.headers), {}, db_pool)
        return {"message": "Access granted"}
    else:
        raise HTTPException(status_code=403, detail="Access denied")


# 转发数据接口
@app.post("/forward-data")
async def forward_data(request):
    ip = request.client.host
    url = "http://example.com/target-endpoint"  # 目标接口URL
    await log_request(ip, dict(request.headers), await request.json(), await
                      get_db_pool())
    response = await forward_post_request(url, dict(request.headers), await
                                          request.json())
    return response.json()


# SQLAlchemy版本
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi_sqlalchemy import DBSessionMiddleware
import aiohttp
import asyncio
import json
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# 数据库配置
DATABASE_URL = "mysql+aiomysql://user:password@localhost/dbname"
engine = create_async_engine(DATABASE_URL)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 添加数据库会话中间件
app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)

# 跨域资源共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定义白名单 IP 表模型
class WhitelistIP(BaseModel):
    ip: str


# 权限校验
async def check_ip_whitelist(ip: str, session: AsyncSession):
    # 假设白名单 IP 存储在 whitelist_ips 表中
    result = await session.execute(
        "SELECT * FROM whitelist_ips WHERE ip = :ip", {"ip": ip})
    return await result.first() is not None


# 接收用户 POST 数据并转发
async def forward_post_request(url: str, headers: dict, json_data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers,
                                json=json_data) as response:
            return await response.text()


# 路由：权限校验
@app.post("/check-permission/")
async def check_permission(ip: str = "127.0.0.1",
                           session: AsyncSession = None):
    if await check_ip_whitelist(ip, session):
        return {"message": "IP is in whitelist"}
    else:
        raise HTTPException(status_code=403, detail="IP is not in whitelist")


# 路由：接收数据并转发
@app.post("/proxy-post/")
async def proxy_post(url: str,
                     headers: dict = {},
                     json_data: dict = {},
                     session: AsyncSession = None):
    # 记录日志
    await session.execute(
        "INSERT INTO logs (ip, headers, json_data) VALUES (:ip, :headers, :json_data)",
        {
            "ip": "127.0.0.1",
            "headers": json.dumps(headers),
            "json_data": json.dumps(json_data)
        },
    )
    await session.commit()

    # 转发请求
    response = await forward_post_request(url, headers, json_data)
    return {"response": response}


# uvicorn main:app --reload
