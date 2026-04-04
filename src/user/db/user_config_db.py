from typing import Optional

from src.common.utils import time_util
from src.storage.sqlite.database import db_execute, db_query
from src.storage.sqlite.models import UserConfig


class _UserConfigDb:
    # 用户配置数据访问层

    @db_query
    def get_config(self, db, user_id: str) -> Optional[UserConfig]:
        # 根据 user_id 查询配置
        return db.query(UserConfig).filter(UserConfig.user_id == user_id).first()

    @db_execute
    def update_config(self, db, user_id: str, model_key: str, enable_thinking: bool) -> bool:
        # 更新或创建用户配置，返回是否成功
        try:
            config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
            if config:
                config.model_key = model_key
                config.enable_thinking = enable_thinking
                config.updated_at = time_util.get_timestamp()
            else:
                config = UserConfig(
                    user_id=user_id,
                    model_key=model_key,
                    enable_thinking=enable_thinking,
                    updated_at=time_util.get_timestamp(),
                )
                db.add(config)
            return True
        except Exception:
            return False

    @db_execute
    def delete_config(self, db, user_id: str) -> bool:
        # 删除用户配置，返回是否成功
        config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
        if config:
            db.delete(config)
            return True
        return False


user_config_db = _UserConfigDb()
