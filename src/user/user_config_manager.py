from src.agent.hooks.entities import ModelConfig
from src.config.config import app_config
from src.user.db.user_config_db import user_config_db


class _UserConfigManager:
    # 用户配置管理器

    def _is_valid_model_key(self, model_key: str) -> bool:
        # 检查 model_key 是否在配置中有效
        models = app_config.get("models", {})
        return model_key in models

    def get_config(self, user_id: str) -> ModelConfig:
        # 获取用户配置，不存在或 model_key 无效则返回默认配置
        config = user_config_db.get_config(user_id)
        if config and self._is_valid_model_key(config.model_key):
            return ModelConfig(
                model_key=config.model_key,
                enable_thinking=config.enable_thinking,
            )
        return ModelConfig(
            model_key=app_config.get_default_model(),
            enable_thinking=True,
        )

    def update_config(self, user_id: str, model_key: str, enable_thinking: bool) -> bool:
        # 更新用户配置
        if not self._is_valid_model_key(model_key):
            return False
        return user_config_db.update_config(user_id, model_key, enable_thinking)


user_config_manager = _UserConfigManager()
