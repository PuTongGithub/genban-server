"""Skills 模块 HTTP 接口控制器"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from src.user.auth import get_current_user_id
from src.modules.skills.entities import (
    SkillListResponse,
    SkillInfo,
    SkillDeleteResponse,
)
from src.modules.skills.skills_manager import skills_manager
from src.modules.skills.exceptions import SkillNotFoundException
from src.common.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("/list")
async def list_skills(
    user_id: str = Depends(get_current_user_id),
) -> SkillListResponse:
    """查询当前用户所有 Skills

    Args:
        user_id: 当前用户ID（由依赖注入）

    Returns:
        用户 Skills 列表，包含 id、name 和 description
    """
    skills = skills_manager.load_all_skills(user_id)
    skill_infos = [
        SkillInfo(id=s.id, name=s.name, description=s.description) for s in skills
    ]
    return SkillListResponse(skills=skill_infos)


@router.get("/content")
async def get_skill_content(
    skill_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """获取指定 Skill 的 SKILL.md 文件内容

    Args:
        skill_id: Skill ID
        user_id: 当前用户ID（由依赖注入）

    Returns:
        SKILL.md 文件内容（纯文本）
    """
    content = skills_manager.get_skill_md_content(user_id, skill_id)

    if content is None:
        logger.warning(f"Skill 不存在，user_id: {user_id}, skill_id: {skill_id}")
        raise HTTPException(
            status_code=404, detail=f"Skill 不存在或 SKILL.md 文件不存在: {skill_id}"
        )

    return PlainTextResponse(content)


@router.delete("/delete")
async def delete_skill(
    skill_id: str,
    user_id: str = Depends(get_current_user_id),
) -> SkillDeleteResponse:
    """删除指定 Skill

    Args:
        skill_id: Skill ID
        user_id: 当前用户ID（由依赖注入）

    Returns:
        删除结果
    """

    try:
        success = skills_manager.delete_user_skill(user_id, skill_id)
        return SkillDeleteResponse(success=success)
    except SkillNotFoundException as e:
        logger.warning(
            f"Skill 不存在，无法删除，user_id: {user_id}, skill_id: {skill_id}"
        )
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception(f"Skill 删除失败，user_id: {user_id}, skill_id: {skill_id}")
        raise HTTPException(status_code=500, detail="删除失败")
