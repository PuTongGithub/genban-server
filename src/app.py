"""FastAPI应用入口"""

import atexit
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.common.async_executor import AsyncExecutor
from src.gateway.routers import register_all_routers


# 注册优雅停机
atexit.register(AsyncExecutor.stop_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    yield
    AsyncExecutor.stop_all()


# 创建FastAPI应用，注册所有路由
app = FastAPI(lifespan=lifespan)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

for router in register_all_routers():
    app.include_router(router)
