"""Immutable input models cho Agent và workflow kho dữ liệu."""

from dataclasses import dataclass

from src.application.data_warehouse_workflows.output import ValidationIssue
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.data_source.entities import DataSource
from src.domain.requirement.entities import Requirement
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class GetAnalysisStatusInput:
    """Yêu cầu đọc trạng thái analysis của Project."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class ReanalyzeProjectInput:
    """Yêu cầu phân tích lại input đã thay đổi."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class GenerateDataModelInput:
    """Yêu cầu tạo Data Model đầu tiên."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class RegenerateDataModelInput:
    """Yêu cầu tạo lại và ghi đè Data Model hiện hành."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class CreateAiEditProposalInput:
    """Yêu cầu AI chỉnh model và tạo Human Review proposal."""

    project_id: EntityID
    instruction: str


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    """Một message công khai được dùng làm lịch sử hội thoại Agent."""

    role: str
    content: str


@dataclass(frozen=True, slots=True)
class CreateAgentTurnInput:
    """Yêu cầu Agent trả câu hỏi làm rõ hoặc proposal."""

    project_id: EntityID
    instruction: str
    history: tuple[ConversationMessage, ...] = ()
    turn_id: EntityID | None = None


@dataclass(frozen=True, slots=True)
class RequirementContext:
    """Bản sao Requirement tối thiểu truyền qua outbound port."""

    id: EntityID
    title: str
    description: str
    requirement_type: RequirementType
    priority: RequirementPriority


@dataclass(frozen=True, slots=True)
class RawRequirementAnalysisInput:
    """Raw Requirement cần cấu trúc hóa."""

    raw_requirement: str


@dataclass(frozen=True, slots=True)
class AnalyticalAnalysisInput:
    """Context tạo AnalyticalRequirements."""

    requirements: tuple[RequirementContext, ...]
    data_sources: tuple[DataSource, ...]


@dataclass(frozen=True, slots=True)
class DataWarehouseDesignInput:
    """Input cho một lần gọi DWDesignAgent."""

    requirements: tuple[Requirement, ...]
    analytical_requirements: tuple[AnalyticalRequirement, ...]
    data_sources: tuple[DataSource, ...]
    failed_dbml: str | None = None
    validation_issues: tuple[ValidationIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class RevisionDesignInput:
    """Input chỉnh sửa Data Model bằng DWDesignAgent."""

    requirements: tuple[Requirement, ...]
    analytical_requirements: tuple[AnalyticalRequirement, ...]
    data_sources: tuple[DataSource, ...]
    current_dbml: str
    instruction: str | None = None
    validation_issues: tuple[ValidationIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class ConversationDesignInput:
    """Context đầy đủ cho một lượt hội thoại thiết kế kho dữ liệu."""

    revision: RevisionDesignInput
    history: tuple[ConversationMessage, ...] = ()
