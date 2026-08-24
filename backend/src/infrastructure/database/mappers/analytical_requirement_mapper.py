"""Mapper chuyển đổi dữ liệu giữa AnalyticalRequirement Domain Entity và AnalyticalRequirementModel Persistence."""

from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import AggregationMethod
from src.infrastructure.database.models.analytical_requirement import AnalyticalRequirementModel


class AnalyticalRequirementMapper:
    """Mapper thực hiện chuyển đổi giữa AnalyticalRequirement Entity và AnalyticalRequirementModel."""

    @staticmethod
    def to_domain(model: AnalyticalRequirementModel) -> AnalyticalRequirement:
        """Chuyển đổi từ AnalyticalRequirementModel (Persistence) sang AnalyticalRequirement (Domain Entity)."""
        agg = AggregationMethod(model.aggregation_method) if model.aggregation_method else None
        return AnalyticalRequirement(
            id=model.id,
            requirement_id=model.requirement_id,
            metric=model.metric,
            dimension=model.dimension,
            time_granularity=model.time_granularity,
            aggregation_method=agg,
            grain=model.grain,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: AnalyticalRequirement) -> AnalyticalRequirementModel:
        """Chuyển đổi từ AnalyticalRequirement (Domain Entity) sang AnalyticalRequirementModel (Persistence)."""
        agg_str = (
            (
                str(entity.aggregation_method.value)
                if hasattr(entity.aggregation_method, "value")
                else entity.aggregation_method
            )
            if entity.aggregation_method
            else None
        )

        return AnalyticalRequirementModel(
            id=entity.id,
            requirement_id=entity.requirement_id,
            metric=entity.metric,
            dimension=entity.dimension,
            time_granularity=entity.time_granularity,
            aggregation_method=agg_str,
            grain=entity.grain,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: AnalyticalRequirementModel, entity: AnalyticalRequirement) -> AnalyticalRequirementModel:
        """Cập nhật dữ liệu từ AnalyticalRequirement Entity sang AnalyticalRequirementModel đã tồn tại."""
        agg_str = (
            (
                str(entity.aggregation_method.value)
                if hasattr(entity.aggregation_method, "value")
                else entity.aggregation_method
            )
            if entity.aggregation_method
            else None
        )

        model.requirement_id = entity.requirement_id
        model.metric = entity.metric
        model.dimension = entity.dimension
        model.time_granularity = entity.time_granularity
        model.aggregation_method = agg_str
        model.grain = entity.grain
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        return model
