"""Các quy tắc cấu trúc và Kimball tối thiểu trên PyDBML AST."""

from src.application.data_warehouse_workflows.output import (
    ValidationIssue,
    ValidationIssueCode,
    ValidationSeverity,
)


class PrimaryKeyRule:
    """Mỗi bảng phải có khóa xác định grain ổn định."""

    def evaluate(self, database: object) -> tuple[ValidationIssue, ...]:
        """Báo lỗi cho bảng không có cột primary key."""
        return tuple(
            ValidationIssue(
                code=ValidationIssueCode.TABLE_PRIMARY_KEY_MISSING,
                severity=ValidationSeverity.ERROR,
                title="Bảng chưa có primary key",
                description="Bảng phải có primary key để xác định grain.",
                table_name=table.name,
            )
            for table in getattr(database, "tables", ())
            if not any(getattr(column, "pk", False) for column in table.columns)
        )


class DuplicateColumnRule:
    """Không cho phép một bảng khai báo trùng tên cột."""

    def evaluate(self, database: object) -> tuple[ValidationIssue, ...]:
        """Báo lỗi cho tên cột lặp, không phân biệt hoa thường."""
        return tuple(
            ValidationIssue(
                code=ValidationIssueCode.TABLE_COLUMN_NAME_DUPLICATED,
                severity=ValidationSeverity.ERROR,
                title="Tên cột bị trùng",
                description="Bảng có nhiều cột trùng tên, không phân biệt hoa thường.",
                table_name=table.name,
            )
            for table in getattr(database, "tables", ())
            if _has_duplicate_columns(table)
        )


class DuplicateRelationshipRule:
    """Không cho phép hai relationship có cùng endpoints."""

    def evaluate(self, database: object) -> tuple[ValidationIssue, ...]:
        """Tìm endpoint trùng trong parsed references."""
        seen: set[frozenset[str]] = set()
        issues: list[ValidationIssue] = []
        for reference in getattr(database, "refs", ()):
            endpoints = _reference_endpoints(reference)
            if endpoints in seen:
                issues.append(_duplicate_relationship_issue())
            seen.add(endpoints)
        return tuple(issues)


class FactRelationshipRule:
    """Fact table nên liên kết ít nhất một dimension."""

    def evaluate(self, database: object) -> tuple[ValidationIssue, ...]:
        """Trả warning để không chặn mô hình không theo naming convention."""
        related = _related_tables(database)
        return tuple(
            ValidationIssue(
                code=ValidationIssueCode.FACT_DIMENSION_RELATIONSHIP_MISSING,
                severity=ValidationSeverity.WARNING,
                title="Fact table chưa liên kết dimension",
                description="Fact table nên có ít nhất một relationship tới dimension.",
                table_name=table.name,
            )
            for table in getattr(database, "tables", ())
            if table.name.casefold().startswith("fact_") and table.name not in related
        )


def _duplicate_relationship_issue() -> ValidationIssue:
    """Tạo issue dùng chung cho relationship trùng endpoint."""
    return ValidationIssue(
        code=ValidationIssueCode.RELATIONSHIP_DUPLICATED,
        severity=ValidationSeverity.ERROR,
        title="Relationship bị trùng",
        description="Hai relationship đang khai báo cùng endpoints.",
    )


def _reference_endpoints(reference: object) -> frozenset[str]:
    """Tạo key không phụ thuộc chiều từ một PyDBML reference."""
    columns = [*getattr(reference, "col1", ()), *getattr(reference, "col2", ())]
    return frozenset(
        f"{column.table.name}.{column.name}"
        for column in columns
        if getattr(column, "table", None) is not None
    )


def _has_duplicate_columns(table: object) -> bool:
    """Kiểm tra tên cột lặp trong một parsed table."""
    names = [column.name.casefold() for column in getattr(table, "columns", ())]
    return len(names) != len(set(names))


def _related_tables(database: object) -> set[str]:
    """Thu thập mọi bảng xuất hiện trong relationship."""
    return {
        endpoint.split(".", maxsplit=1)[0]
        for reference in getattr(database, "refs", ())
        for endpoint in _reference_endpoints(reference)
    }
