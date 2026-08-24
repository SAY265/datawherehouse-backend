"""Mapper chuyển đổi dữ liệu giữa DataModel Domain Entity và DataModelModel Persistence."""

from src.domain.data_model.entities import DataModel
from src.infrastructure.database.models.data_model import DataModelModel


class DataModelMapper:
    """Mapper thực hiện chuyển đổi giữa DataModel Entity và DataModelModel."""

    @staticmethod
    def to_domain(model: DataModelModel) -> DataModel:
        """Chuyển đổi từ DataModelModel (Persistence) sang DataModel (Domain Entity)."""
        return DataModel(
            id=model.id,
            project_id=model.project_id,
            dbml=model.dbml,
            revision=model.revision,
            generated_from_requirement_revision=model.generated_from_requirement_revision,
            generated_from_source_revision=model.generated_from_source_revision,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: DataModel) -> DataModelModel:
        """Chuyển đổi từ DataModel (Domain Entity) sang DataModelModel (Persistence)."""
        return DataModelModel(
            id=entity.id,
            project_id=entity.project_id,
            dbml=entity.dbml,
            revision=entity.revision,
            generated_from_requirement_revision=entity.generated_from_requirement_revision,
            generated_from_source_revision=entity.generated_from_source_revision,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: DataModelModel, entity: DataModel) -> DataModelModel:
        """Cập nhật dữ liệu từ DataModel Entity sang DataModelModel đã tồn tại."""
        model.project_id = entity.project_id
        model.dbml = entity.dbml
        model.revision = entity.revision
        model.generated_from_requirement_revision = entity.generated_from_requirement_revision
        model.generated_from_source_revision = entity.generated_from_source_revision
        model.updated_at = entity.updated_at
        return model
