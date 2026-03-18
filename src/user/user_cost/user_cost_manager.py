from typing import Optional
from src.user.user_cost.user_cost_db import user_cost_db
from src.common.logger import get_logger

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
    ) -> bool:
        # 记录Token消耗（按天聚合）
        try:
            success = user_cost_db.create(
                user_id=user_id,
                model_key=model_key,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )
            if success:
                logger.debug(
                    f"记录Token消耗成功，user_id: {user_id}, model_key: {model_key}, total_tokens: {total_tokens}"
                )
            else:
                logger.warning(f"记录Token消耗失败，user_id: {user_id}")
            return success
        except Exception:
            logger.exception(f"记录Token消耗异常，user_id: {user_id}")
            return False

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
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 按用户和模型统计Token消耗
        return user_cost_db.get_user_model_stats(start_date, end_date)

    def get_daily_cost_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 按天统计Token消耗
        return user_cost_db.get_daily_stats(start_date, end_date)

    def get_cost_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        # 获取完整的Token消耗报表
        user_stats = self.get_user_cost_stats(start_date, end_date)
        model_stats = self.get_model_cost_stats(start_date, end_date)
        user_model_stats = self.get_user_model_cost_stats(start_date, end_date)
        daily_stats = self.get_daily_cost_stats(start_date, end_date)

        # 计算总计
        total_input = sum(s["total_input_tokens"] for s in user_stats)
        total_output = sum(s["total_output_tokens"] for s in user_stats)
        total_tokens = sum(s["total_tokens"] for s in user_stats)
        total_calls = sum(s["call_count"] for s in user_stats)

        return {
            "summary": {
                "total_input_tokens": total_input,
                "total_output_tokens": total_output,
                "total_tokens": total_tokens,
                "total_calls": total_calls,
            },
            "by_user": user_stats,
            "by_model": model_stats,
            "by_user_model": user_model_stats,
            "by_day": daily_stats,
        }


user_cost_manager = _UserCostManager()
