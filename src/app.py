"""FastAPI应用入口"""

import atexit
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.common.async_executor import AsyncExecutor
from src.gateway.routers import routers
from src.assistant.web.stream_manager import stream_manager


# 注册优雅停机
def stop() -> None:
    """停止所有异步任务"""
    AsyncExecutor.stop_all()
    stream_manager.stop()


atexit.register(stop)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    yield
    stop()


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

for router in routers:
    app.include_router(router)
