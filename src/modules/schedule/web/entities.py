"""日程模块 Web 层实体定义"""

from typing import Optional

from pydantic import BaseModel


class ScheduleInfo(BaseModel):
    """日程信息"""

    id: int
    title: str
    content: str
    cron_expression: str
    remind_enabled: bool
    enabled: bool
    onetime: bool
    created_at: int
    updated_at: int


class ScheduleListResponse(BaseModel):
    """日程列表响应"""

    schedules: list[ScheduleInfo]
    error: str = ""


class ScheduleCreateRequest(BaseModel):
    """创建日程请求"""

    title: str
    content: str = ""
    cron_expression: str
    remind_enabled: bool = True
    onetime: bool = False


class ScheduleCreateResponse(BaseModel):
    """创建日程响应"""

    success: bool = False
    schedule_id: int = 0
    error: str = ""


class ScheduleUpdateRequest(BaseModel):
    """更新日程请求"""

    schedule_id: int
    title: Optional[str] = None
    content: Optional[str] = None
    cron_expression: Optional[str] = None
    remind_enabled: Optional[bool] = None
    onetime: Optional[bool] = None


class ScheduleUpdateResponse(BaseModel):
    """更新日程响应"""

    success: bool = False
    error: str = ""


class ScheduleDeleteRequest(BaseModel):
    """删除日程请求"""

    schedule_id: int


class ScheduleDeleteResponse(BaseModel):
    """删除日程响应"""

    success: bool = False
    error: str = ""
