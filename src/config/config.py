"""配置管理模块"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

from src.storage.file.file_storage import file_storage
from src.config.exceptions import (
    EnvConfigNotFoundException,
    ModelConfigNotFoundException,
)


class EnvConfig:
    """环境配置管理器"""

    def __init__(self):
        """初始化环境配置，加载.env文件"""
        load_dotenv()

    def get(self, key: str) -> str:
        """获取环境变量"""
        value = os.getenv(key)
        if not value:
            raise EnvConfigNotFoundException(key)
        return value


class AppConfig:
    """应用配置管理器"""

    def __init__(self):
        """初始化应用配置"""
        app_config_path = Path(__file__).parent / "jsons/app_config.json"
        with open(app_config_path, "r", encoding="utf-8") as file:
            self.config = json.load(file)

    def get(self, key: str):
        """获取配置项"""
        return self.config.get(key)

    def get_default_model(self) -> str:
        """获取默认模型"""
        for key, value in self.config["models"].items():
            if value.get("default", False):
                return key
        raise ModelConfigNotFoundException("not found default model")

    def get_model_config(self, model_key: str) -> dict:
        """获取模型配置"""
        models = self.get("models")
        if model_key not in models:
            raise ModelConfigNotFoundException(model_key)
        return models[model_key]


class FileConfig:
    """文件配置管理器 - 从文件读取配置，初始化时加载到内存"""

    def __init__(self):
        """初始化文件配置，加载所有配置文件到内存"""
        self._project_root = Path(__file__).parent.parent.parent
        self._private_key = self._load_private_key()
        self._public_key = self._load_public_key()

    def _load_private_key(self) -> str:
        """从文件加载RSA私钥内容"""
        private_key_path = self._project_root / "keys" / "private_key.pem"
        return file_storage.read_text(private_key_path)

    def _load_public_key(self) -> str:
        """从文件加载RSA公钥内容"""
        public_key_path = self._project_root / "keys" / "public_key.pem"
        return file_storage.read_text(public_key_path)

    def get_private_key(self) -> str:
        """获取RSA私钥内容（从内存返回）"""
        return self._private_key

    def get_public_key(self) -> str:
        """获取RSA公钥内容（从内存返回）"""
        return self._public_key


# 全局配置实例
env_config = EnvConfig()
app_config = AppConfig()
file_config = FileConfig()
