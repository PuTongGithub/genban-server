from typing import Optional
from threading import Lock
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from src.storage.sqlite.database import db_execute, db_query
from src.user.db.models import UserCost
from src.common.utils import time_util


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
    ) -> bool:
        # 创建或更新Token消耗记录（按天聚合）
        with self._lock:
            try:
                date = time_util.get_now_str(time_util.STR_FORMATTER_DATE_WITH_MARKS)
                now = time_util.get_timestamp()

                # 查找当天是否已有记录
                existing = (
                    db.query(UserCost)
                    .filter(
                        UserCost.user_id == user_id,
                        UserCost.model_key == model_key,
                        UserCost.date == date,
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
            func.sum(UserCost.call_count).label("call_count"),
        ).group_by(UserCost.user_id)

        if start_date is not None:
            query = query.filter(UserCost.date >= start_date)
        if end_date is not None:
            query = query.filter(UserCost.date <= end_date)

        results = query.all()
        return [
            {
                "user_id": r.user_id,
                "total_input_tokens": r.total_input or 0,
                "total_output_tokens": r.total_output or 0,
                "total_tokens": r.total or 0,
                "call_count": r.call_count or 0,
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
            func.sum(UserCost.call_count).label("call_count"),
        ).group_by(UserCost.model_key)

        if start_date is not None:
            query = query.filter(UserCost.date >= start_date)
        if end_date is not None:
            query = query.filter(UserCost.date <= end_date)

        results = query.all()
        return [
            {
                "model_key": r.model_key,
                "total_input_tokens": r.total_input or 0,
                "total_output_tokens": r.total_output or 0,
                "total_tokens": r.total or 0,
                "call_count": r.call_count or 0,
            }
            for r in results
        ]

    @db_query
    def get_user_model_stats(
        self,
        db,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 按用户和模型统计Token消耗
        query = db.query(
            UserCost.user_id,
            UserCost.model_key,
            func.sum(UserCost.input_tokens).label("total_input"),
            func.sum(UserCost.output_tokens).label("total_output"),
            func.sum(UserCost.total_tokens).label("total"),
            func.sum(UserCost.call_count).label("call_count"),
        ).group_by(UserCost.user_id, UserCost.model_key)

        if start_date is not None:
            query = query.filter(UserCost.date >= start_date)
        if end_date is not None:
            query = query.filter(UserCost.date <= end_date)

        results = query.all()
        return [
            {
                "user_id": r.user_id,
                "model_key": r.model_key,
                "total_input_tokens": r.total_input or 0,
                "total_output_tokens": r.total_output or 0,
                "total_tokens": r.total or 0,
                "call_count": r.call_count or 0,
            }
            for r in results
        ]

    @db_query
    def get_daily_stats(
        self,
        db,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        # 按天统计Token消耗
        query = (
            db.query(
                UserCost.date,
                func.sum(UserCost.input_tokens).label("total_input"),
                func.sum(UserCost.output_tokens).label("total_output"),
                func.sum(UserCost.total_tokens).label("total"),
                func.sum(UserCost.call_count).label("call_count"),
            )
            .group_by(UserCost.date)
            .order_by(UserCost.date)
        )

        if start_date is not None:
            query = query.filter(UserCost.date >= start_date)
        if end_date is not None:
            query = query.filter(UserCost.date <= end_date)

        results = query.all()
        return [
            {
                "date": r.date,
                "total_input_tokens": r.total_input or 0,
                "total_output_tokens": r.total_output or 0,
                "total_tokens": r.total or 0,
                "call_count": r.call_count or 0,
            }
            for r in results
        ]


user_cost_db = _UserCostDb()
