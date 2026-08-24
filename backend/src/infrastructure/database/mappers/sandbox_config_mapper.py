"""Ánh xạ SandboxConfig và mã hóa credential tại persistence boundary."""

from src.domain.sandbox.entities import SandboxConfig
from src.domain.sandbox.enums import SandboxDbType, SandboxStatus
from src.infrastructure.database.models.sandbox_config import SandboxConfigModel
from src.infrastructure.security.credential_cipher import CredentialCipher


class SandboxConfigMapper:
    """Mapper có dependency cipher cho trường password."""

    def __init__(self, cipher: CredentialCipher) -> None:
        """Khởi tạo mapper với cipher dùng chung của ứng dụng."""
        self._cipher = cipher

    def to_model(self, entity: SandboxConfig) -> SandboxConfigModel:
        """Tạo ORM model mới và mã hóa password."""
        return SandboxConfigModel(
            id=entity.id,
            project_id=entity.project_id,
            db_type=entity.db_type.value,
            host=entity.host,
            port=entity.port,
            database_name=entity.database_name,
            username=entity.username,
            password=self._cipher.encrypt(entity.password),
            schema_name=entity.schema_name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def update_model(
        self,
        model: SandboxConfigModel,
        entity: SandboxConfig,
    ) -> SandboxConfigModel:
        """Cập nhật trường mutable, giữ nguyên created_at."""
        model.db_type = entity.db_type.value
        model.host = entity.host
        model.port = entity.port
        model.database_name = entity.database_name
        model.username = entity.username
        model.password = self._cipher.encrypt(entity.password)
        model.schema_name = entity.schema_name
        model.updated_at = entity.updated_at
        return model

    def to_domain(
        self,
        model: SandboxConfigModel,
        password: str | None = None,
    ) -> SandboxConfig:
        """Khôi phục Domain entity, ưu tiên password rõ vừa được lưu."""
        return SandboxConfig(
            id=model.id,
            project_id=model.project_id,
            db_type=SandboxDbType(model.db_type),
            host=model.host,
            port=model.port,
            database_name=model.database_name,
            username=model.username,
            password=password if password is not None else self._cipher.decrypt(model.password),
            schema_name=model.schema_name,
            status=SandboxStatus.CONFIGURED,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
