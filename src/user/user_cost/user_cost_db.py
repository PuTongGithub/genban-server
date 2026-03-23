from threading import Lock
from typing import Optional

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from src.common.logger import get_logger
from src.common.utils import time_util
from src.storage.sqlite.database import db_execute, db_query
from src.storage.sqlite.models import UserCost

logger = get_logger(__name__)


class _UserCostDb:
    # 用户Token消耗数据访问层（按天统计）

    def __init__(self) -> None:
        self._lock = Lock()

    @db_execute
    def create(
        self,
        db,
        user_id: str,
        model_key: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        type: str = "assistant",  # assistant 或 conversation
    ) -> bool:
        # 创建或更新Token消耗记录（按天聚合）
        with self._lock:
            try:
                date = time_util.get_now_str(time_util.STR_FORMATTER_DATE_WITH_MARKS)
                now = time_util.get_timestamp()

                # 查找当天是否已有记录（同类型）
                existing = (
                    db.query(UserCost)
                    .filter(
                        UserCost.user_id == user_id,
                        UserCost.model_key == model_key,
                        UserCost.date == date,
                        UserCost.type == type,
                    )
                    .first()
                )

                if existing:
                    # 更新现有记录
                    existing.input_tokens += input_tokens
                    existing.output_tokens += output_tokens
                    existing.total_tokens += total_tokens
                    existing.call_count += 1
                    existing.updated_at = now
                else:
                    # 创建新记录
                    cost = UserCost(
                        user_id=user_id,
                        model_key=model_key,
                        date=date,
                        type=type,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        total_tokens=total_tokens,
                        call_count=1,
                        created_at=now,
                        updated_at=now,
                    )
                    db.add(cost)
                return True
            except SQLAlchemyError:
                logger.exception("创建或更新用户Token消耗记录失败")
                return False

    @db_query
    def get_total_by_user_id(self, db, user_id: str) -> dict:
        # 获取用户总消耗统计
        result = (
            db.query(
                func.sum(UserCost.input_tokens).label("total_input"),
                func.sum(UserCost.output_tokens).label("total_output"),
                func.sum(UserCost.total_tokens).label("total"),
                func.sum(UserCost.call_count).label("total_calls"),
            )
            .filter(UserCost.user_id == user_id)
            .first()
        )

        return {
            "user_id": user_id,
            "total_input_tokens": result.total_input or 0,
            "total_output_tokens": result.total_output or 0,
            "total_tokens": result.total or 0,
            "total_calls": result.total_calls or 0,
        }

    @db_query
    def get_stats_by_user(
        self,
        db,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 按用户统计Token消耗
        query = db.query(
            UserCost.user_id,
            func.sum(UserCost.input_tokens).label("total_input"),
            func.sum(UserCost.output_tokens).label("total_output"),
            func.sum(UserCost.total_tokens).label("total"),
            func.sum(UserCost.call_count).label("total_calls"),
        )

        if start_date:
            query = query.filter(UserCost.date >= start_date)
        if end_date:
            query = query.filter(UserCost.date <= end_date)

        results = query.group_by(UserCost.user_id).all()

        return [
            {
                "user_id": r.user_id,
                "total_input_tokens": r.total_input or 0,
                "total_output_tokens": r.total_output or 0,
                "total_tokens": r.total or 0,
                "total_calls": r.total_calls or 0,
            }
            for r in results
        ]

    @db_query
    def get_stats_by_model(
        self,
        db,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 按模型统计Token消耗
        query = db.query(
            UserCost.model_key,
            func.sum(UserCost.input_tokens).label("total_input"),
            func.sum(UserCost.output_tokens).label("total_output"),
            func.sum(UserCost.total_tokens).label("total"),
            func.sum(UserCost.call_count).label("total_calls"),
        )

        if start_date:
            query = query.filter(UserCost.date >= start_date)
        if end_date:
            query = query.filter(UserCost.date <= end_date)

        results = query.group_by(UserCost.model_key).all()

        return [
            {
                "model_key": r.model_key,
                "total_input_tokens": r.total_input or 0,
                "total_output_tokens": r.total_output or 0,
                "total_tokens": r.total or 0,
                "total_calls": r.total_calls or 0,
            }
            for r in results
        ]

    @db_query
    def get_user_model_cost_stats(
        self,
        db,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 获取用户按模型的消耗统计
        query = db.query(
            UserCost.model_key,
            func.sum(UserCost.input_tokens).label("total_input"),
            func.sum(UserCost.output_tokens).label("total_output"),
            func.sum(UserCost.total_tokens).label("total"),
            func.sum(UserCost.call_count).label("total_calls"),
        ).filter(UserCost.user_id == user_id)

        if start_date:
            query = query.filter(UserCost.date >= start_date)
        if end_date:
            query = query.filter(UserCost.date <= end_date)

        results = query.group_by(UserCost.model_key).all()

        return [
            {
                "model_key": r.model_key,
                "total_input_tokens": r.total_input or 0,
                "total_output_tokens": r.total_output or 0,
                "total_tokens": r.total or 0,
                "total_calls": r.total_calls or 0,
            }
            for r in results
        ]

    @db_query
    def get_stats_by_type(
        self,
        db,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 按类型统计Token消耗
        query = db.query(
            UserCost.type,
            func.sum(UserCost.input_tokens).label("total_input"),
            func.sum(UserCost.output_tokens).label("total_output"),
            func.sum(UserCost.total_tokens).label("total"),
            func.sum(UserCost.call_count).label("total_calls"),
        )

        if start_date:
            query = query.filter(UserCost.date >= start_date)
        if end_date:
            query = query.filter(UserCost.date <= end_date)

        results = query.group_by(UserCost.type).all()

        return [
            {
                "type": r.type,
                "total_input_tokens": r.total_input or 0,
                "total_output_tokens": r.total_output or 0,
                "total_tokens": r.total or 0,
                "total_calls": r.total_calls or 0,
            }
            for r in results
        ]

    @db_query
    def get_user_type_cost_stats(
        self,
        db,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 获取用户按类型的消耗统计
        query = db.query(
            UserCost.type,
            func.sum(UserCost.input_tokens).label("total_input"),
            func.sum(UserCost.output_tokens).label("total_output"),
            func.sum(UserCost.total_tokens).label("total"),
            func.sum(UserCost.call_count).label("total_calls"),
        ).filter(UserCost.user_id == user_id)

        if start_date:
            query = query.filter(UserCost.date >= start_date)
        if end_date:
            query = query.filter(UserCost.date <= end_date)

        results = query.group_by(UserCost.type).all()

        return [
            {
                "type": r.type,
                "total_input_tokens": r.total_input or 0,
                "total_output_tokens": r.total_output or 0,
                "total_tokens": r.total or 0,
                "total_calls": r.total_calls or 0,
            }
            for r in results
        ]


# 全局实例
user_cost_db = _UserCostDb()
