import json
from typing import Callable, Optional

from src.common.logger import get_logger
from src.common.utils.rsa_util import RsaUtil
from src.config.config import file_config
from src.gateway.im.manager.credential_db import credential_db
from src.gateway.im.manager.entities import (
    DuplicateEnabledCredentialError,
    IMCredentialConfig,
)
from src.storage.sqlite.models import IMCredential

logger = get_logger(__name__)


class _CredentialManager:
    """IM 凭证管理器，负责凭证的加密存储和解密读取"""

    def __init__(self) -> None:
        self._rsa_util = RsaUtil(
            private_key_content=file_config.get_private_key(),
            public_key_content=file_config.get_public_key(),
        )
        self._update_callbacks: list[Callable[[IMCredentialConfig, bool], None]] = []

    def register_update_callback(
        self, callback: Callable[[IMCredentialConfig, bool], None]
    ) -> None:
        """注册凭证更新回调"""
        self._update_callbacks.append(callback)

    def _trigger_update_callbacks(
        self, credential: IMCredentialConfig, is_deleted: bool = False
    ) -> None:
        """触发凭证更新回调"""
        for callback in self._update_callbacks:
            try:
                callback(credential, is_deleted)
            except Exception:
                logger.exception(f"触发凭证更新回调失败: callback={str(callback)}")

    def encrypt_data(self, data: dict) -> str:
        """加密数据"""
        json_str = json.dumps(data, ensure_ascii=False)
        return self._rsa_util.encrypt(json_str)

    def decrypt_data(self, encrypted_data: str) -> dict:
        """解密数据"""
        json_str = self._rsa_util.decrypt(encrypted_data)
        return json.loads(json_str)

    def _to_config(self, credential: IMCredential) -> IMCredentialConfig:
        """将数据库模型转换为配置实体"""
        return IMCredentialConfig(
            id=credential.id,
            user_id=credential.user_id,
            channel_type=credential.channel_type,
            credential_data=credential.credential_data,
            identity_data=credential.identity_data,
            enabled=credential.enabled,
            created_at=credential.created_at,
            updated_at=credential.updated_at,
        )

    def get_credentials(self, user_id: str) -> list[IMCredentialConfig]:
        """获取用户所有凭证"""
        credentials = credential_db.get_credentials(user_id)
        return [self._to_config(c) for c in credentials]

    def get_credential(self, credential_id: int, user_id: str) -> Optional[IMCredentialConfig]:
        """获取单个凭证"""
        credential = credential_db.get_credential(credential_id, user_id)
        if credential:
            return self._to_config(credential)
        return None

    def get_credential_by_type(
        self, user_id: str, channel_type: str
    ) -> Optional[IMCredentialConfig]:
        """按渠道类型获取凭证"""
        credential = credential_db.get_credential_by_type(user_id, channel_type)
        if credential:
            return self._to_config(credential)
        return None

    def _check_duplicate_enabled(
        self, user_id: str, channel_type: str, exclude_id: int | None = None
    ) -> None:
        """检查同一用户、同一渠道类型是否已存在启用凭证，存在则抛出异常"""
        if credential_db.has_enabled_credential_by_type(user_id, channel_type, exclude_id):
            raise DuplicateEnabledCredentialError(user_id, channel_type)

    def create_credential(
        self, user_id: str, channel_type: str, credential_data: dict
    ) -> Optional[IMCredentialConfig]:
        """创建凭证，credential_data 为明文字典，自动加密存储。如果同类型已有启用凭证则抛出异常。"""
        # 检查是否已存在启用凭证
        self._check_duplicate_enabled(user_id, channel_type)

        encrypted_data = self.encrypt_data(credential_data)
        credential = credential_db.create_credential(user_id, channel_type, encrypted_data)
        if credential:
            config = self._to_config(credential)
            self._trigger_update_callbacks(config)
            return config
        return None

    def update_credential(
        self,
        credential_id: int,
        user_id: str,
        credential_data: Optional[dict] = None,
        enabled: Optional[bool] = None,
    ) -> bool:
        """更新凭证，credential_data 为明文字典，自动加密存储。如果启用时同类型已有其他启用凭证则抛出异常。"""
        # 如果要启用凭证，检查是否已存在其他启用凭证
        if enabled is True:
            existing = credential_db.get_credential(credential_id, user_id)
            if existing:
                self._check_duplicate_enabled(user_id, existing.channel_type, credential_id)

        encrypted_data = None
        if credential_data is not None:
            encrypted_data = self.encrypt_data(credential_data)
        credential = credential_db.update_credential(
            credential_id, user_id, encrypted_data, None, enabled
        )
        if credential:
            self._trigger_update_callbacks(self._to_config(credential))
            return True
        return False

    def update_identity_data(
        self,
        credential_id: int,
        user_id: str,
        identity_data: dict,
    ) -> bool:
        """更新身份识别数据，identity_data 为明文字典，自动加密存储"""
        encrypted_data = self.encrypt_data(identity_data)
        credential = credential_db.update_credential(
            credential_id, user_id, None, encrypted_data, None
        )
        return credential is not None

    def delete_credential(self, credential_id: int, user_id: str) -> bool:
        """删除凭证，删除前触发回调通知渠道"""
        # 先获取凭证信息用于回调
        credential = credential_db.get_credential(credential_id, user_id)
        if credential:
            config = self._to_config(credential)
            self._trigger_update_callbacks(config, is_deleted=True)

        return credential_db.delete_credential(credential_id, user_id)

    def list_enabled_credentials(self) -> list[IMCredentialConfig]:
        """获取所有启用的凭证（用于启动渠道）"""
        credentials = credential_db.list_enabled_credentials()
        return [self._to_config(c) for c in credentials]

    def get_decrypted_credential_data(self, credential: IMCredentialConfig) -> dict:
        """获取解密后的凭证数据"""
        return self.decrypt_data(credential.credential_data)

    def get_decrypted_identity_data(self, credential: IMCredentialConfig) -> Optional[dict]:
        """获取解密后的身份识别数据"""
        if credential.identity_data:
            return self.decrypt_data(credential.identity_data)
        return None


credential_manager = _CredentialManager()
