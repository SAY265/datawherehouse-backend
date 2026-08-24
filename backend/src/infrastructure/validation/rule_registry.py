"""Registry cho các quy tắc validation Data Model."""

from typing import Protocol

from src.application.data_warehouse_workflows.output import ValidationIssue


class DataModelValidationRule(Protocol):
    """Contract của một quy tắc validation deterministic."""

    def evaluate(self, database: object) -> tuple[ValidationIssue, ...]:
        """Đánh giá parsed DBML mà không thực hiện I/O."""


class ValidationRuleRegistry:
    """Tập quy tắc có thứ tự để ValidationEngine thực thi."""

    def __init__(self, rules: tuple[DataModelValidationRule, ...] = ()) -> None:
        self._rules = list(rules)

    def register(self, rule: DataModelValidationRule) -> None:
        """Đăng ký quy tắc ở cuối pipeline."""
        self._rules.append(rule)

    def evaluate(self, database: object) -> tuple[ValidationIssue, ...]:
        """Gộp issues của toàn bộ quy tắc đã đăng ký."""
        return tuple(issue for rule in self._rules for issue in rule.evaluate(database))
