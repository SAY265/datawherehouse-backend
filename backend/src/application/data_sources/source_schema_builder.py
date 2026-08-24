"""Build immutable source schema metadata from profiling and classification results."""

from dataclasses import dataclass, replace

from src.application.data_sources.source_analysis_models import (
    AnalyzedSourceSchema,
    ColumnClassificationOutput,
    ProfiledSource,
    ProfiledTableSource,
    SourceFileAnalysisInput,
)
from src.domain.data_source.column_profile import ColumnProfile, LogicalTypeDecision
from src.domain.data_source.column_type_inference import is_identifier_like
from src.domain.data_source.enums import ColumnDataType
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata

CLASSIFIER_FALLBACK_THRESHOLD = 0.7


@dataclass(frozen=True, slots=True)
class SourceSchemaBuildInput:
    source_index: int
    source: SourceFileAnalysisInput
    profile: ProfiledSource
    decisions: tuple[tuple[LogicalTypeDecision, ...], ...]
    classifications: dict[str, ColumnClassificationOutput]


@dataclass(frozen=True, slots=True)
class _TableBuildInput:
    source_index: int
    table_index: int
    table: ProfiledTableSource
    decisions: tuple[LogicalTypeDecision, ...]
    classifications: dict[str, ColumnClassificationOutput]


@dataclass(frozen=True, slots=True)
class _ColumnBuildInput:
    profile: ColumnProfile
    decision: LogicalTypeDecision
    classification: ColumnClassificationOutput | None
    declared: ColumnMetadata | None


def build_source_schema(data: SourceSchemaBuildInput) -> AnalyzedSourceSchema:
    tables = tuple(
        _build_table(
            _TableBuildInput(
                data.source_index,
                table_index,
                table,
                table_decisions,
                data.classifications,
            )
        )
        for table_index, (table, table_decisions) in enumerate(
            zip(data.profile.tables, data.decisions, strict=True)
        )
    )
    return AnalyzedSourceSchema(data.source.source_id, SchemaMetadata(tables=tables))


def _build_table(data: _TableBuildInput) -> TableMetadata:
    declared = data.table.declared_columns or (None,) * len(data.table.columns)
    columns = tuple(
        _build_column(
            _ColumnBuildInput(
                column,
                decision,
                data.classifications.get(
                    f"{data.source_index}:{data.table_index}:{column_index}"
                ),
                declared[column_index],
            )
        )
        for column_index, (column, decision) in enumerate(
            zip(data.table.columns, data.decisions, strict=True)
        )
    )
    return TableMetadata(data.table.table_name, columns)


def _build_column(data: _ColumnBuildInput) -> ColumnMetadata:
    final_type = data.decision.data_type
    if data.classification and data.classification.confidence >= CLASSIFIER_FALLBACK_THRESHOLD:
        final_type = data.classification.data_type
    profile = data.profile
    non_null_count = profile.total_rows - profile.null_count
    is_unique = non_null_count > 0 and profile.distinct_count == non_null_count
    metadata = _inferred_metadata(profile, final_type, is_unique)
    if data.declared is None:
        return metadata
    return replace(
        data.declared,
        null_count=profile.null_count,
        distinct_count=profile.distinct_count,
        distinct_values=(
            profile.distinct_values if data.declared.data_type is ColumnDataType.CATEGORY else ()
        ),
        is_unique_candidate=is_unique,
        is_key_candidate=data.declared.primary_key or (is_unique and is_identifier_like(profile)),
    )


def _inferred_metadata(
    profile: ColumnProfile,
    final_type: ColumnDataType,
    is_unique: bool,
) -> ColumnMetadata:
    return ColumnMetadata(
        name=profile.name,
        data_type=final_type,
        nullable=profile.null_count > 0,
        null_count=profile.null_count,
        distinct_count=profile.distinct_count,
        distinct_values=profile.distinct_values if final_type is ColumnDataType.CATEGORY else (),
        is_unique_candidate=is_unique,
        is_key_candidate=is_unique and is_identifier_like(profile),
    )
