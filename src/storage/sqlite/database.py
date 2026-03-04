from contextlib import contextmanager
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.common.utils.path_util import get_data_dir

# 数据库文件路径
db_path = get_data_dir() / "genban.db"
db_path.parent.mkdir(parents=True, exist_ok=True)

# 创建引擎
engine = create_engine(f"sqlite:///{db_path}", echo=False)

# 创建会话类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


@contextmanager
def get_db():
    # 获取数据库会话上下文管理器，自动处理提交、回滚和关闭
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def db_execute(func):
    # 数据库操作装饰器，自动处理会话和异常
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with get_db() as db:
            return func(self, db, *args, **kwargs)
    return wrapper


def db_query(func):
    # 数据库查询装饰器，自动处理会话（只读，不提交）
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        db = SessionLocal()
        try:
            return func(self, db, *args, **kwargs)
        finally:
            db.close()
    return wrapper
