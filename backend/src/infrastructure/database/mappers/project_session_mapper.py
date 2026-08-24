"""Mapper chuyển đổi dữ liệu giữa ProjectSession Domain Entity và ProjectSessionModel Persistence."""

from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.enums import SessionStatus
from src.infrastructure.database.models.project_session import ProjectSessionModel


class ProjectSessionMapper:
    """Mapper thực hiện chuyển đổi giữa ProjectSession Entity và ProjectSessionModel."""

    @staticmethod
    def to_domain(model: ProjectSessionModel) -> ProjectSession:
        """Chuyển đổi từ ProjectSessionModel (Persistence) sang ProjectSession (Domain Entity)."""
        return ProjectSession(
            id=model.id,
            project_id=model.project_id,
            user_id=model.user_id,
            title=model.title or "Untitled Session",
            status=SessionStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: ProjectSession) -> ProjectSessionModel:
        """Chuyển đổi từ ProjectSession (Domain Entity) sang ProjectSessionModel (Persistence)."""
        return ProjectSessionModel(
            id=entity.id,
            project_id=entity.project_id,
            user_id=entity.user_id,
            title=entity.title,
            status=str(entity.status.value if hasattr(entity.status, "value") else entity.status),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: ProjectSessionModel, entity: ProjectSession) -> ProjectSessionModel:
        """Cập nhật dữ liệu từ ProjectSession Entity sang ProjectSessionModel đã tồn tại."""
        model.project_id = entity.project_id
        model.user_id = entity.user_id
        model.title = entity.title
        model.status = str(entity.status.value if hasattr(entity.status, "value") else entity.status)
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        return model
