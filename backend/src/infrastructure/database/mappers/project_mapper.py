"""Mapper chuyển đổi dữ liệu giữa Project Domain Entity và ProjectModel Persistence."""

from src.domain.project.entities import Project
from src.domain.project.enums import ProjectStatus
from src.infrastructure.database.models.project import ProjectModel


class ProjectMapper:
    """Mapper thực hiện chuyển đổi giữa Project Entity và ProjectModel."""

    @staticmethod
    def to_domain(model: ProjectModel) -> Project:
        """Chuyển đổi từ ProjectModel (Persistence) sang Project (Domain Entity)."""
        return Project(
            id=model.id,
            name=model.name,
            requirement=model.requirement,
            user_id=model.user_id,
            description=model.description,
            domain=model.domain,
            status=ProjectStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Project) -> ProjectModel:
        """Chuyển đổi từ Project (Domain Entity) sang ProjectModel (Persistence)."""
        return ProjectModel(
            id=entity.id,
            name=entity.name,
            requirement=entity.requirement,
            user_id=entity.user_id,
            description=entity.description,
            domain=entity.domain,
            status=str(entity.status.value if hasattr(entity.status, "value") else entity.status),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: ProjectModel, entity: Project) -> ProjectModel:
        """Cập nhật dữ liệu từ Project Entity sang ProjectModel đã tồn tại."""
        model.name = entity.name
        model.requirement = entity.requirement
        model.user_id = entity.user_id
        model.description = entity.description
        model.domain = entity.domain
        model.status = str(entity.status.value if hasattr(entity.status, "value") else entity.status)
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        return model
