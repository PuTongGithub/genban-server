"""用户模块测试路由"""

from fastapi import APIRouter


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/test")
async def test():
    """测试接口"""
    return {"message": "test"}
