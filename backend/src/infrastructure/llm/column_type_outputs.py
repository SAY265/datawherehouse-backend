"""Structured output schema riêng cho ColumnTypeClassifier."""

from pydantic import BaseModel, ConfigDict, Field
from src.domain.data_source.enums import ColumnDataType


class ColumnTypeClassificationItem(BaseModel):
    """Một quyết định logical type gắn opaque column reference."""

    model_config = ConfigDict(extra="forbid")
    reference: str = Field(min_length=1)
    data_type: ColumnDataType
    confidence: float = Field(ge=0, le=1)


class ColumnTypeClassificationResult(BaseModel):
    """Batch kết quả classifier."""

    model_config = ConfigDict(extra="forbid")
    columns: list[ColumnTypeClassificationItem]
