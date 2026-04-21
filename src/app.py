"""FastAPI应用入口"""

import atexit
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.assistant import modules
from src.common.async_executor import AsyncExecutor
from src.common.logger import get_logger, setup_logging
from src.common.thread_executor import ThreadExecutor
from src.gateway.im.manager.im_manager import IMManager
from src.gateway.web.routers import routers
from src.gateway.web.stream_manager import StreamManager
from src.modules.schedule.scheduler.scheduler import Scheduler

# 初始化日志系统
setup_logging()
logger = get_logger(__name__)


# 注册优雅停机
def stop() -> None:
    """停止所有异步任务"""
    logger.info("应用正在关闭...")
    AsyncExecutor.stop_all()
    ThreadExecutor.stop_all()
    StreamManager.get_instance().stop()
    Scheduler.get_instance().shutdown()
    logger.info("应用已关闭")
    logging.shutdown()


atexit.register(stop)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("lifespan 启动")
    Scheduler.get_instance()
    IMManager.get_instance()
    StreamManager.get_instance()
    modules.init()

    yield
    logger.info("lifespan 关闭")
    stop()


# 创建FastAPI应用，注册所有路由
app = FastAPI(lifespan=lifespan)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Cookie"],
)

for router in routers:
    app.include_router(router)
