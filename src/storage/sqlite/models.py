"""SQLite 数据库实体模型统一管理

此模块集中管理所有数据库表实体定义，便于统一维护和创建表结构。
"""

from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.sqlite.database import Base, engine

# =============================================================================
# 用户相关模型
# =============================================================================


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)


class UserToken(Base):
    """用户Token模型 - 支持多端同时在线"""

    __tablename__ = "user_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    token: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)


class UserConfig(Base):
    """用户配置模型"""

    __tablename__ = "user_configs"

    user_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    model_key: Mapped[str] = mapped_column(String, nullable=False)
    enable_thinking: Mapped[bool] = mapped_column(Boolean, nullable=False)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False)


class UserCost(Base):
    """用户Token消耗记录模型（按天统计）"""

    __tablename__ = "user_costs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    model_key: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False, index=True)  # 日期格式：YYYY-MM-DD
    type: Mapped[str] = mapped_column(
        String, nullable=False, default="assistant"
    )  # assistant 或 conversation
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    call_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # 当天调用次数
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False)


# =============================================================================
# 记忆相关模型
# =============================================================================


class ConversationMemory(Base):
    """Conversation Memory 数据模型 - 存储对话摘要（简化版，每个用户一条记录）"""

    __tablename__ = "conversation_memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), nullable=False, unique=True, index=True)
    end_chat_id = Column(String(64), nullable=False)
    end_chat_time = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(Integer, nullable=False)


# =============================================================================
# IM 凭证相关模型
# =============================================================================


class IMCredential(Base):
    """IM 凭证模型 - 存储 IM 渠道凭证"""

    __tablename__ = "im_credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    channel_type: Mapped[str] = mapped_column(String, nullable=False)
    credential_data: Mapped[str] = mapped_column(Text, nullable=False)
    identity_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False)


# =============================================================================
# 日程相关模型
# =============================================================================


class Schedule(Base):
    """日程模型 - 存储用户日程安排"""

    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    cron_expression: Mapped[str] = mapped_column(String, nullable=False)
    remind_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    onetime: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False)


# =============================================================================
# 创建所有表
# =============================================================================

Base.metadata.create_all(bind=engine)
