"""Mapper chuyển đổi dữ liệu giữa DataSource Domain Entity và DataSourceModel Persistence."""

from typing import Any

from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType, RelationshipType
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    RelationshipMetadata,
    SchemaMetadata,
    TableMetadata,
)
from src.infrastructure.database.models.data_source import DataSourceModel


class DataSourceMapper:
    """Mapper thực hiện chuyển đổi giữa DataSource Entity và DataSourceModel."""

    @staticmethod
    def schema_metadata_to_dict(schema: SchemaMetadata | None) -> dict[str, Any] | None:
        """Chuyển đổi SchemaMetadata Value Object sang dict JSONB."""
        if not schema:
            return None

        tables_data = []
        for table in schema.tables:
            cols_data = []
            for col in table.columns:
                cols_data.append(
                    {
                        "name": col.name,
                        "data_type": col.data_type,
                        "primary_key": col.primary_key,
                        "nullable": col.nullable,
                        "unique": col.unique,
                        "foreign_key_reference": col.foreign_key_reference,
                        "default_value": col.default_value,
                        "constraints": list(col.constraints),
                        "description": col.description,
                    }
                )
            tables_data.append({"name": table.name, "columns": cols_data})

        rels_data = []
        for rel in schema.relationships:
            rel_type = str(rel.type.value) if hasattr(rel.type, "value") else rel.type
            rels_data.append(
                {
                    "from_column": rel.from_column,
                    "to_column": rel.to_column,
                    "type": rel_type,
                }
            )

        return {"tables": tables_data, "relationships": rels_data}

    @staticmethod
    def dict_to_schema_metadata(data: dict[str, Any] | None) -> SchemaMetadata | None:
        """Chuyển đổi dict JSONB từ database sang SchemaMetadata Value Object."""
        if not data:
            return None

        tables_list = []
        for tbl in data.get("tables", []):
            cols_list = []
            for col in tbl.get("columns", []):
                cols_list.append(
                    ColumnMetadata(
                        name=col["name"],
                        data_type=col["data_type"],
                        primary_key=col.get("primary_key", False),
                        nullable=col.get("nullable", True),
                        unique=col.get("unique", False),
                        foreign_key_reference=col.get("foreign_key_reference"),
                        default_value=col.get("default_value"),
                        constraints=tuple(col.get("constraints", ())),
                        description=col.get("description"),
                    )
                )
            tables_list.append(TableMetadata(name=tbl["name"], columns=tuple(cols_list)))

        rels_list = []
        for rel in data.get("relationships", []):
            rels_list.append(
                RelationshipMetadata(
                    from_column=rel["from_column"],
                    to_column=rel["to_column"],
                    type=RelationshipType(rel["type"]),
                )
            )

        return SchemaMetadata(tables=tuple(tables_list), relationships=tuple(rels_list))

    @classmethod
    def to_domain(cls, model: DataSourceModel) -> DataSource:
        """Chuyển đổi từ DataSourceModel (Persistence) sang DataSource (Domain Entity)."""
        return DataSource(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            location=model.location,
            type=DataSourceType(model.type),
            description=model.description,
            schema_metadata=cls.dict_to_schema_metadata(model.schema_metadata),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_model(cls, entity: DataSource) -> DataSourceModel:
        """Chuyển đổi từ DataSource (Domain Entity) sang DataSourceModel (Persistence)."""
        return DataSourceModel(
            id=entity.id,
            project_id=entity.project_id,
            name=entity.name,
            location=entity.location,
            type=str(entity.type.value if hasattr(entity.type, "value") else entity.type),
            description=entity.description,
            schema_metadata=cls.schema_metadata_to_dict(entity.schema_metadata),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @classmethod
    def update_model(cls, model: DataSourceModel, entity: DataSource) -> DataSourceModel:
        """Cập nhật dữ liệu từ DataSource Entity sang DataSourceModel đã tồn tại."""
        model.project_id = entity.project_id
        model.name = entity.name
        model.location = entity.location
        model.type = str(entity.type.value if hasattr(entity.type, "value") else entity.type)
        model.description = entity.description
        model.schema_metadata = cls.schema_metadata_to_dict(entity.schema_metadata)
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        return model
