"""Typed outputs không làm rò Domain entity qua Agent boundary."""

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.shared.types import EntityID

if TYPE_CHECKING:
    from src.application.data_models.output import ChangeProposalDetailOutput


class ValidationSeverity(StrEnum):
    """Mức độ của một vấn đề validation."""

    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationIssueCode(StrEnum):
    """Mã ổn định định danh từng quy tắc validation Data Model."""

    DBML_SYNTAX_INVALID = "DBML_SYNTAX_INVALID"
    TABLE_PRIMARY_KEY_MISSING = "TABLE_PRIMARY_KEY_MISSING"
    TABLE_COLUMN_NAME_DUPLICATED = "TABLE_COLUMN_NAME_DUPLICATED"
    RELATIONSHIP_DUPLICATED = "RELATIONSHIP_DUPLICATED"
    FACT_DIMENSION_RELATIONSHIP_MISSING = "FACT_DIMENSION_RELATIONSHIP_MISSING"


class RecommendedWorkflowAction(StrEnum):
    """Hành động workflow tiếp theo dành cho UI."""

    NONE = "NONE"
    ANALYZE_CHANGES = "ANALYZE_CHANGES"
    UPDATE_DATA_MODEL = "UPDATE_DATA_MODEL"


@dataclass(frozen=True, slots=True)
class GeneratedRequirement:
    """Requirement do LLM sinh, chưa phải Domain entity."""

    title: str
    description: str
    requirement_type: RequirementType
    priority: RequirementPriority


@dataclass(frozen=True, slots=True)
class GeneratedAnalyticalRequirement:
    """Analytical Requirement do LLM sinh."""

    source_requirement_id: EntityID
    metric: str
    dimension: str
    time_granularity: str
    aggregation_method: str
    grain: str


@dataclass(frozen=True, slots=True)
class GeneratedDbml:
    """DBML trả về từ đúng một invocation của DWDesignAgent."""

    dbml: str


class AgentTurnKind(StrEnum):
    """Loại kết quả công khai của một lượt Agent."""

    CLARIFICATION = "clarification"
    PROPOSAL = "proposal"


@dataclass(frozen=True, slots=True)
class ConversationDesignResult:
    """Kết quả trực tiếp từ Agent trước bước persistence."""

    kind: AgentTurnKind
    question: str | None = None
    dbml: str | None = None
    summary: str | None = None


@dataclass(frozen=True, slots=True)
class AgentTurnOutput:
    """Kết quả application của lượt Agent đã qua persistence."""

    kind: AgentTurnKind
    question: str | None = None
    proposal: "ChangeProposalDetailOutput | None" = None
    summary: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Một lỗi hoặc cảnh báo deterministic của Data Model."""

    code: ValidationIssueCode
    severity: ValidationSeverity
    title: str
    description: str
    table_name: str = ""
    column_name: str = ""


@dataclass(frozen=True, slots=True)
class AnalysisStatusOutput:
    """Trạng thái outdated được tính trực tiếp từ revision."""

    requirement_analysis_outdated: bool
    source_analysis_outdated: bool
    data_model_outdated: bool
    data_model_exists: bool
    recommended_action: RecommendedWorkflowAction
