"""Profile và quyết định logical type thuần Domain."""

from dataclasses import dataclass, field

from src.domain.data_source.enums import ColumnDataType


@dataclass(frozen=True, slots=True)
class ColumnProfile:
    """Các thống kê tối thiểu dùng để hiểu logical type của cột."""

    name: str
    physical_type: str
    sample_values: tuple[str, ...] = field(default_factory=tuple)
    distinct_values: tuple[str, ...] = field(default_factory=tuple)
    null_count: int = 0
    distinct_count: int = 0
    total_rows: int = 0
    average_length: float = 0
    is_fixed_length: bool = False
    has_leading_zero: bool = False
    date_match_ratio: float = 0
    datetime_match_ratio: float = 0
    top_value_ratio: float = 0

    @property
    def distinct_ratio(self) -> float:
        """Tỷ lệ distinct trên các dòng không NULL."""
        non_null_count = self.total_rows - self.null_count
        return self.distinct_count / non_null_count if non_null_count else 0


@dataclass(frozen=True, slots=True)
class LogicalTypeDecision:
    """Candidate logical type và độ chắc chắn của rule engine."""

    data_type: ColumnDataType
    confidence: float
