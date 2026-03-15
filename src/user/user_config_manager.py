from src.agent.hooks.entities import ModelConfig
from src.config.config import app_config
from src.user.db.user_config_db import user_config_db


class _UserConfigManager:
    # 用户配置管理器

    def get_config(self, user_id: str) -> ModelConfig:
        # 获取用户配置，不存在则返回默认配置
        config = user_config_db.get_config(user_id)
        if config:
            return ModelConfig(
                model_key=config.model_key,
                enable_thinking=config.enable_thinking,
            )
        return ModelConfig(
            model_key=app_config.get_default_model(),
            enable_thinking=True,
        )

    def update_config(
        self, user_id: str, model_key: str, enable_thinking: bool
    ) -> bool:
        # 更新用户配置
        return user_config_db.update_config(user_id, model_key, enable_thinking)


user_config_manager = _UserConfigManager()
