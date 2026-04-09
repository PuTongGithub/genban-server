from typing import Optional

from src.common.utils import time_util
from src.storage.sqlite.database import db_execute, db_query
from src.storage.sqlite.models import IMCredential


class _CredentialDb:
    # IM 凭证数据访问层

    @db_query
    def get_credentials(self, db, user_id: str) -> list[IMCredential]:
        # 获取用户所有凭证
        return db.query(IMCredential).filter(IMCredential.user_id == user_id).all()

    @db_query
    def get_credential(self, db, credential_id: int, user_id: str) -> Optional[IMCredential]:
        # 获取单个凭证
        return (
            db.query(IMCredential)
            .filter(IMCredential.id == credential_id, IMCredential.user_id == user_id)
            .first()
        )

    @db_query
    def get_credential_by_type(self, db, user_id: str, channel_type: str) -> Optional[IMCredential]:
        # 按渠道类型获取凭证
        return (
            db.query(IMCredential)
            .filter(IMCredential.user_id == user_id, IMCredential.channel_type == channel_type)
            .first()
        )

    @db_execute
    def create_credential(
        self, db, user_id: str, channel_type: str, credential_data: str
    ) -> Optional[IMCredential]:
        # 创建凭证，返回创建的凭证对象
        try:
            now = time_util.get_timestamp()
            credential = IMCredential(
                user_id=user_id,
                channel_type=channel_type,
                credential_data=credential_data,
                enabled=True,
                created_at=now,
                updated_at=now,
            )
            db.add(credential)
            db.flush()
            db.refresh(credential)
            return credential
        except Exception:
            return None

    @db_execute
    def update_credential(
        self,
        db,
        credential_id: int,
        user_id: str,
        credential_data: Optional[str] = None,
        identity_data: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Optional[IMCredential]:
        # 更新凭证，返回更新后的凭证对象
        credential = (
            db.query(IMCredential)
            .filter(IMCredential.id == credential_id, IMCredential.user_id == user_id)
            .first()
        )
        if not credential:
            return None
        if credential_data is not None:
            credential.credential_data = credential_data
        if identity_data is not None:
            credential.identity_data = identity_data
        if enabled is not None:
            credential.enabled = enabled
        credential.updated_at = time_util.get_timestamp()
        return credential

    @db_execute
    def delete_credential(self, db, credential_id: int, user_id: str) -> bool:
        # 删除凭证，返回是否成功
        credential = (
            db.query(IMCredential)
            .filter(IMCredential.id == credential_id, IMCredential.user_id == user_id)
            .first()
        )
        if credential:
            db.delete(credential)
            return True
        return False

    @db_query
    def list_enabled_credentials(self, db) -> list[IMCredential]:
        # 获取所有启用的凭证
        return db.query(IMCredential).filter(IMCredential.enabled.is_(True)).all()

    @db_query
    def has_enabled_credential_by_type(
        self, db, user_id: str, channel_type: str, exclude_id: int | None = None
    ) -> bool:
        # 检查同一用户、同一渠道类型是否存在启用凭证（排除指定ID）
        query = db.query(IMCredential).filter(
            IMCredential.user_id == user_id,
            IMCredential.channel_type == channel_type,
            IMCredential.enabled.is_(True),
        )
        if exclude_id is not None:
            query = query.filter(IMCredential.id != exclude_id)
        return query.first() is not None


credential_db = _CredentialDb()
