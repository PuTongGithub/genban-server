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

# 创建表
Base.metadata.create_all(bind=engine)
