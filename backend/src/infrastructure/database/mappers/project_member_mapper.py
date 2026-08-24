"""Mapper chuyển đổi dữ liệu giữa ProjectMember Domain Entity và ProjectMemberModel Persistence."""

from src.domain.project.entities import ProjectMember
from src.domain.project.enums import ProjectRole
from src.infrastructure.database.models.project_member import ProjectMemberModel


class ProjectMemberMapper:
    """Mapper thực hiện chuyển đổi giữa ProjectMember Entity và ProjectMemberModel."""

    @staticmethod
    def to_domain(model: ProjectMemberModel) -> ProjectMember:
        """Chuyển đổi từ ProjectMemberModel (Persistence) sang ProjectMember (Domain Entity)."""
        return ProjectMember(
            id=model.id,
            project_id=model.project_id,
            user_id=model.user_id,
            role=ProjectRole(model.role),
            joined_at=model.joined_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: ProjectMember) -> ProjectMemberModel:
        """Chuyển đổi từ ProjectMember (Domain Entity) sang ProjectMemberModel (Persistence)."""
        return ProjectMemberModel(
            id=entity.id,
            project_id=entity.project_id,
            user_id=entity.user_id,
            role=str(entity.role.value if hasattr(entity.role, "value") else entity.role),
            joined_at=entity.joined_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: ProjectMemberModel, entity: ProjectMember) -> ProjectMemberModel:
        """Cập nhật dữ liệu từ ProjectMember Entity sang ProjectMemberModel đã tồn tại."""
        model.project_id = entity.project_id
        model.user_id = entity.user_id
        model.role = str(entity.role.value if hasattr(entity.role, "value") else entity.role)
        model.joined_at = entity.joined_at
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        return model
