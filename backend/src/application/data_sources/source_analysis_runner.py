"""Coordinate source profiling, domain inference, and ambiguous-column classification."""

from src.application.data_sources.source_analysis_models import (
    AnalyzedSourceSchema,
    ColumnClassificationInput,
    ColumnClassificationOutput,
    ProfiledSource,
    SourceFileAnalysisInput,
)
from src.application.data_sources.source_analysis_ports import (
    IColumnTypeClassifier,
    ISourceFileInspector,
)
from src.application.data_sources.source_schema_builder import SourceSchemaBuildInput, build_source_schema
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.column_profile import LogicalTypeDecision
from src.domain.data_source.column_type_inference import infer_logical_type

RULE_CLASSIFIER_THRESHOLD = 0.8
MAX_CLASSIFIER_BATCH_SIZE = 50


class SourceAnalysisRunner:
    def __init__(self, inspector: ISourceFileInspector, classifier: IColumnTypeClassifier) -> None:
        self._inspector = inspector
        self._classifier = classifier

    async def analyze(
        self,
        sources: tuple[SourceFileAnalysisInput, ...],
    ) -> tuple[AnalyzedSourceSchema, ...]:
        """Profile every source and classify only low-confidence inferred columns."""
        profiles = tuple(self._inspector.profile(item.content, item.filename) for item in sources)
        decisions = tuple(
            tuple(tuple(infer_logical_type(column) for column in table.columns) for table in source.tables)
            for source in profiles
        )
        classifications = await self._classify_ambiguous(profiles, decisions)
        return tuple(
            build_source_schema(
                SourceSchemaBuildInput(index, source, profile, decision, classifications)
            )
            for index, (source, profile, decision) in enumerate(
                zip(sources, profiles, decisions, strict=True)
            )
        )

    async def _classify_ambiguous(
        self,
        profiles: tuple[ProfiledSource, ...],
        decisions: tuple[tuple[tuple[LogicalTypeDecision, ...], ...], ...],
    ) -> dict[str, ColumnClassificationOutput]:
        inputs = _classification_inputs(profiles, decisions)
        outputs: dict[str, ColumnClassificationOutput] = {}
        for start in range(0, len(inputs), MAX_CLASSIFIER_BATCH_SIZE):
            batch = inputs[start : start + MAX_CLASSIFIER_BATCH_SIZE]
            classified = await self._classifier.classify(batch)
            _validate_classifications(batch, classified)
            outputs.update((item.reference, item) for item in classified)
        return outputs


def _classification_inputs(
    profiles: tuple[ProfiledSource, ...],
    decisions: tuple[tuple[tuple[LogicalTypeDecision, ...], ...], ...],
) -> tuple[ColumnClassificationInput, ...]:
    inputs = []
    for source_index, (source, source_decisions) in enumerate(zip(profiles, decisions, strict=True)):
        for table_index, (table, table_decisions) in enumerate(
            zip(source.tables, source_decisions, strict=True)
        ):
            for column_index, (column, decision) in enumerate(
                zip(table.columns, table_decisions, strict=True)
            ):
                if table.declared_columns is None and decision.confidence < RULE_CLASSIFIER_THRESHOLD:
                    reference = f"{source_index}:{table_index}:{column_index}"
                    inputs.append(ColumnClassificationInput(reference, column, decision.data_type))
    return tuple(inputs)


def _validate_classifications(
    inputs: tuple[ColumnClassificationInput, ...],
    outputs: tuple[ColumnClassificationOutput, ...],
) -> None:
    expected = {item.reference for item in inputs}
    actual = [item.reference for item in outputs]
    if set(actual) != expected or len(actual) != len(set(actual)):
        raise InfrastructureException(
            ErrorCode.LLM_ERROR, "Classifier trả reference cột không hợp lệ."
        )
