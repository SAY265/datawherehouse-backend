"""Sinh DDL theo dialect từ cây cú pháp PyDBML."""

import sqlglot
from sqlglot import exp
from src.application.data_models.i_data_model_service import IDataModelDdlGenerator
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.sandbox.enums import SandboxDbType
from src.infrastructure.codegen.dbml_parser import parse_dbml
from typing_extensions import override

_SQLGLOT_DIALECTS = {
    "postgresql": "postgres",
    "postgres": "postgres",
    "snowflake": "snowflake",
    "bigquery": "bigquery",
}


class PyDbmlDdlGenerator(IDataModelDdlGenerator):
    """Sinh DDL bằng PyDBML và chuẩn hóa bằng SQLGlot."""

    @override
    def generate_ddl(self, dbml: str, db_type: SandboxDbType) -> str:
        """Sinh script DDL cho dialect được hỗ trợ."""
        target = _resolve_dialect(db_type)
        database = parse_dbml(dbml)
        expressions = order_by_dependency(sqlglot.parse(database.sql, read="sqlite"))
        statements = [item.sql(dialect=target, pretty=True) for item in expressions]
        return ";\n\n".join(statements).strip() + ";"


def _resolve_dialect(db_type: SandboxDbType) -> str:
    """Ánh xạ loại database nghiệp vụ sang SQLGlot dialect."""
    target = _SQLGLOT_DIALECTS.get(db_type.value.casefold())
    if target is not None:
        return target
    supported = ", ".join(sorted(_SQLGLOT_DIALECTS))
    raise BusinessException(
        code=ErrorCode.UNSUPPORTED_DDL_DIALECT,
        message=f"Database type '{db_type.value}' chưa được hỗ trợ. Hiện có: {supported}.",
    )


def order_by_dependency(expressions: list[exp.Expression]) -> list[exp.Expression]:
    """Sắp xếp CREATE TABLE theo phụ thuộc khóa ngoại."""
    creates, dependencies, others = _index_expressions(expressions)
    ordered: list[exp.Expression] = []
    emitted: set[str] = set()
    remaining = list(creates)
    while remaining:
        ready = [name for name in remaining if dependencies[name] <= emitted] or remaining
        for name in ready:
            ordered.append(creates[name])
            emitted.add(name)
        remaining = [name for name in remaining if name not in emitted]
    return [*ordered, *others]


def _index_expressions(expressions: list[exp.Expression]) -> tuple[dict, dict, list]:
    """Lập chỉ mục biểu thức và phụ thuộc bảng."""
    creates: dict[str, exp.Expression] = {}
    dependencies: dict[str, set[str]] = {}
    others: list[exp.Expression] = []
    for expression in expressions:
        table = expression.find(exp.Table) if isinstance(expression, exp.Create) else None
        if table is None:
            others.append(expression)
            continue
        creates[table.name] = expression
        dependencies[table.name] = _referenced_tables(expression, table.name)
    return creates, dependencies, others


def _referenced_tables(expression: exp.Expression, own_name: str) -> set[str]:
    """Lấy tên bảng được tham chiếu bởi một CREATE TABLE."""
    return {
        table.name
        for foreign_key in expression.find_all(exp.ForeignKey)
        if (table := foreign_key.find(exp.Table)) is not None and table.name != own_name
    }
