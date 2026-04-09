"""路由集中注册

在此集中导入并注册所有模块的路由
"""

from typing import List

from fastapi import APIRouter

from src.gateway.web import assistant_controller
from src.modules.file_system import file_system_controller
from src.modules.im.web import im_controller
from src.modules.schedule.web import schedule_controller
from src.modules.settings import setting_controller
from src.modules.skills import skills_controller
from src.user import user_controller

# 全局路由列表
routers: List[APIRouter] = []
routers.append(user_controller.router)
routers.append(setting_controller.router)
routers.append(assistant_controller.router)
routers.append(file_system_controller.router)
routers.append(skills_controller.router)
routers.append(schedule_controller.router)
routers.append(im_controller.router)
