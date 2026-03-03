"""FastAPI应用入口"""

import atexit
from contextlib import asynccontextmanager
from fastapi import FastAPI
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
for router in register_all_routers():
    app.include_router(router)
