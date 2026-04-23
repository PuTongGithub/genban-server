"""日程模块路由"""

from fastapi import APIRouter, Depends

from src.common.logger import get_logger
from src.modules.schedule.component.schedule_manager import schedule_manager
from src.modules.schedule.web.entities import (
    ScheduleCreateRequest,
    ScheduleCreateResponse,
    ScheduleDeleteRequest,
    ScheduleDeleteResponse,
    ScheduleInfo,
    ScheduleListResponse,
    ScheduleUpdateRequest,
    ScheduleUpdateResponse,
)
from src.user.auth import get_current_user_id

logger = get_logger(__name__)
router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.get("/list")
async def list_schedules(
    user_id: str = Depends(get_current_user_id),
) -> ScheduleListResponse:
    """查询日程列表（只返回启用的日程）"""
    try:
        schedules = schedule_manager.list_schedules(user_id, enabled_only=True)
        schedule_infos = [
            ScheduleInfo(
                id=s.id,
                title=s.title,
                content=s.content or "",
                cron_expression=s.cron_expression,
                remind_enabled=s.remind_enabled,
                enabled=s.enabled,
                onetime=s.onetime,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in schedules
        ]
        return ScheduleListResponse(schedules=schedule_infos)
    except Exception as e:
        logger.exception(f"查询日程列表失败，user_id: {user_id}")
        return ScheduleListResponse(schedules=[], error=str(e))


@router.post("/create")
async def create_schedule(
    request: ScheduleCreateRequest,
    user_id: str = Depends(get_current_user_id),
) -> ScheduleCreateResponse:
    """创建日程"""
    try:
        created = schedule_manager.create_schedule(
            user_id=user_id,
            title=request.title,
            cron_expression=request.cron_expression,
            content=request.content,
            remind_enabled=request.remind_enabled,
            onetime=request.onetime,
        )
        return ScheduleCreateResponse(success=True, schedule_id=created.id)
    except Exception as e:
        logger.exception(f"创建日程失败，user_id: {user_id}")
        return ScheduleCreateResponse(error=str(e))


@router.post("/update")
async def update_schedule(
    request: ScheduleUpdateRequest,
    user_id: str = Depends(get_current_user_id),
) -> ScheduleUpdateResponse:
    """更新日程"""
    try:
        updated = schedule_manager.update_schedule(
            user_id=user_id,
            schedule_id=request.schedule_id,
            title=request.title,
            content=request.content,
            cron_expression=request.cron_expression,
            remind_enabled=request.remind_enabled,
            onetime=request.onetime,
        )
        if updated:
            return ScheduleUpdateResponse(success=True)
        else:
            return ScheduleUpdateResponse(success=False, error="日程不存在")
    except Exception as e:
        logger.exception(f"更新日程失败，user_id: {user_id}, schedule_id: {request.schedule_id}")
        return ScheduleUpdateResponse(success=False, error=str(e))


@router.post("/delete")
async def delete_schedule(
    request: ScheduleDeleteRequest,
    user_id: str = Depends(get_current_user_id),
) -> ScheduleDeleteResponse:
    """删除日程（软删除）"""
    try:
        success = schedule_manager.delete_schedule(user_id, request.schedule_id)
        if success:
            return ScheduleDeleteResponse(success=True)
        else:
            return ScheduleDeleteResponse(success=False, error="日程不存在")
    except Exception as e:
        logger.exception(f"删除日程失败，user_id: {user_id}, schedule_id: {request.schedule_id}")
        return ScheduleDeleteResponse(success=False, error=str(e))
