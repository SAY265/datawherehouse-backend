"""Facade parse DBML và thực thi các quy tắc validation."""

from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataModelValidationEngine,
)
from src.application.data_warehouse_workflows.output import (
    ValidationIssue,
    ValidationIssueCode,
    ValidationSeverity,
)
from src.common.exceptions.business import BusinessException
from src.infrastructure.codegen.dbml_parser import parse_dbml
from src.infrastructure.validation.rule_registry import ValidationRuleRegistry
from src.infrastructure.validation.structural_rules import (
    DuplicateColumnRule,
    DuplicateRelationshipRule,
    FactRelationshipRule,
    PrimaryKeyRule,
)
from typing_extensions import override


class DbmlValidationEngine(IDataModelValidationEngine):
    """Validation engine deterministic dùng PyDBML parser được duy trì."""

    def __init__(self, registry: ValidationRuleRegistry | None = None) -> None:
        self._registry = registry or _default_registry()

    @override
    def validate(self, dbml: str) -> tuple[ValidationIssue, ...]:
        """Parse DBML rồi chạy các quy tắc cấu trúc và thiết kế."""
        try:
            database = parse_dbml(dbml)
        except BusinessException as exc:
            return (
                ValidationIssue(
                    code=ValidationIssueCode.DBML_SYNTAX_INVALID,
                    severity=ValidationSeverity.ERROR,
                    title="Cú pháp DBML không hợp lệ",
                    description=exc.message,
                ),
            )
        return self._registry.evaluate(database)


def _default_registry() -> ValidationRuleRegistry:
    """Đăng ký bộ quy tắc mặc định theo thứ tự ổn định."""
    return ValidationRuleRegistry(
        (
            PrimaryKeyRule(),
            DuplicateColumnRule(),
            DuplicateRelationshipRule(),
            FactRelationshipRule(),
        )
    )
