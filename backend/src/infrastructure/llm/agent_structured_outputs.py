"""Pydantic schemas cho structured output của từng Agent operation."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator
from src.domain.requirement.enums import RequirementPriority, RequirementType


class GeneratedRequirementItem(BaseModel):
    """Một Requirement có cấu trúc do RequirementAgent sinh."""

    title: str = Field(min_length=1, description="Short requirement title.")
    description: str = Field(min_length=1, description="Complete requirement statement.")
    requirement_type: RequirementType
    priority: RequirementPriority = RequirementPriority.MEDIUM


class RequirementStructureResult(BaseModel):
    """Kết quả operation Raw Requirement thành Requirements."""

    requirements: list[GeneratedRequirementItem]


class AnalyticalRequirementItem(BaseModel):
    """Một Analytical Requirement gắn chính xác Requirement nguồn."""

    source_requirement_id: str = Field(description="Exact UUID from the input.")
    metric: str
    dimension: str
    time_granularity: str
    aggregation_method: Literal["SUM", "AVG", "COUNT", "COUNT_DISTINCT", "MAX", "MIN"]
    grain: str


class AnalyticalRequirementResult(BaseModel):
    """Kết quả operation Requirements và schema thành analytical context."""

    analytical_requirements: list[AnalyticalRequirementItem]


class DbmlRevisionResult(BaseModel):
    """Toàn bộ DBML do một DWDesignAgent invocation sinh."""

    dbml: str = Field(
        min_length=1,
        description="Complete raw DBML document without markdown or commentary.",
    )


class DwConversationResult(BaseModel):
    """Câu hỏi làm rõ hoặc DBML proposal từ một lượt hội thoại."""

    kind: Literal["clarification", "proposal"] = Field(
        description="Choose clarification or proposal."
    )
    question: str | None = Field(
        description="Required key. A concise question for clarification; null for proposal."
    )
    dbml: str | None = Field(
        description="Required key. Complete raw DBML for proposal; null for clarification."
    )
    summary: str = Field(
        min_length=1,
        description=(
            "One or two concise user-facing sentences; no repetition or private reasoning."
        ),
    )

    @model_validator(mode="after")
    def validate_payload(self) -> "DwConversationResult":
        """Bắt buộc đúng payload tương ứng với discriminator."""
        if self.kind == "clarification" and not (self.question or "").strip():
            raise ValueError("Clarification result requires question.")
        if self.kind == "proposal" and not (self.dbml or "").strip():
            raise ValueError("Proposal result requires dbml.")
        return self
