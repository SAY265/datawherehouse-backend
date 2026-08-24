"""Value objects cho miền Sandbox."""

from dataclasses import dataclass, field

from src.domain.shared.value_object import BaseValueObject


@dataclass(frozen=True)
class StatementLog(BaseValueObject):
    """Value object lưu log thực thi của một câu lệnh SQL."""

    statement: str
    is_success: bool
    execution_time_ms: float
    timestamp: str
    error_detail: str | None = None


@dataclass(frozen=True)
class SandboxExecutionResult(BaseValueObject):
    """Value object kết quả thực thi DDL trên Sandbox DB."""

    success: bool
    executed_statements: int
    succeeded_statements: int
    failed_statements: int
    total_duration_ms: float
    logs: tuple[StatementLog, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Đảm bảo danh sách log luôn ở dạng bất biến."""
        object.__setattr__(self, "logs", tuple(self.logs))
