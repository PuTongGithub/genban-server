"""路由集中注册

在此集中导入并注册所有模块的路由
"""

from fastapi import APIRouter
from typing import List

# 导入各模块路由
from src.user.web import user_controller


# 全局路由列表
_routers: List[APIRouter] = []


def register_all_routers() -> List[APIRouter]:
    """注册所有路由并返回路由列表"""
    _routers.append(user_controller.router)
    
    return _routers
