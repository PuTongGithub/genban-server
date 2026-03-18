from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.storage.sqlite.database import Base, engine


# 用户模型
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)


# 用户状态模型
class UserState(Base):
    __tablename__ = "user_states"

    user_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False)
    token: Mapped[str] = mapped_column(String, nullable=False, index=True)
    token_expires_at: Mapped[int] = mapped_column(Integer, nullable=False)


# 用户配置模型
class UserConfig(Base):
    __tablename__ = "user_configs"

    user_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    model_key: Mapped[str] = mapped_column(String, nullable=False)
    enable_thinking: Mapped[bool] = mapped_column(Boolean, nullable=False)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False)


# 用户Token消耗记录模型（按天统计）
class UserCost(Base):
    __tablename__ = "user_costs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    model_key: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )  # 日期格式：YYYY-MM-DD
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    call_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )  # 当天调用次数
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False)


# 创建表
Base.metadata.create_all(bind=engine)
