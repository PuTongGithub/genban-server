from typing import Optional

from src.common.logger import get_logger
from src.user.user_cost.user_cost_db import user_cost_db

logger = get_logger(__name__)


class _UserCostManager:
    # 用户Token消耗管理器（按天统计）

    def record_cost(
        self,
        user_id: str,
        model_key: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        type: str = "assistant",  # assistant 或 conversation
    ) -> bool:
        # 记录Token消耗（按天聚合）
        success = user_cost_db.create(
            user_id=user_id,
            model_key=model_key,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            type=type,
        )
        if success:
            logger.debug(
                f"记录Token消耗成功，user_id: {user_id}, model_key: {model_key}, "
                f"type: {type}, total_tokens: {total_tokens}"
            )
        else:
            logger.warning(f"记录Token消耗失败，user_id: {user_id}")
        return success

    def get_user_total_cost(self, user_id: str) -> dict:
        # 获取用户总消耗
        return user_cost_db.get_total_by_user_id(user_id)

    def get_user_cost_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 按用户统计Token消耗
        return user_cost_db.get_stats_by_user(start_date, end_date)

    def get_model_cost_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 按模型统计Token消耗
        return user_cost_db.get_stats_by_model(start_date, end_date)

    def get_user_model_cost_stats(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 获取用户按模型的消耗统计
        return user_cost_db.get_user_model_cost_stats(user_id, start_date, end_date)

    def get_type_cost_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 按类型统计Token消耗
        return user_cost_db.get_stats_by_type(start_date, end_date)

    def get_user_type_cost_stats(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 获取用户按类型的消耗统计
        return user_cost_db.get_user_type_cost_stats(user_id, start_date, end_date)


# 全局实例
user_cost_manager = _UserCostManager()
