"""Chuẩn hóa DBML do LLM sinh ra trước khi đưa qua ValidationEngine.

Mô hình ngôn ngữ rất hay khai báo cùng một quan hệ hai lần: một lần gắn vào cột
(`col int [ref: > Dim.key]`) và một lần nữa ở cấp tài liệu (`Ref: Fact.col > Dim.key`).
Hai khai báo đó không mâu thuẫn, chỉ là thừa — nhưng `@dbml/core` (thư viện dựng canvas
ERD ở Frontend) từ chối với lỗi "References with same endpoints exist".

Bắt Agent sinh lại vì lỗi này rất tốn kém: mỗi lượt retry là một lần gọi LLM, và thực
nghiệm cho thấy nó lặp đúng thói quen cũ ở cả ba lượt. Bỏ đi dòng thừa là phép biến đổi
xác định, không làm đổi ngữ nghĩa mô hình, nên xử lý ngay tại đây rẻ và chắc chắn hơn.
"""

import re

from lark_dbml import loads
from lark_dbml.lark_dbml_standalone import UnexpectedInput
from src.common.logging import get_logger

logger = get_logger(__name__)

# Khớp một câu `Ref` viết trên một dòng: `Ref: A.col > B.col` hoặc `Ref name: A.col < B.col`.
_INLINE_REF_STATEMENT = re.compile(
    r"""^\s*Ref\s*[\w"'`]*\s*:\s*
        (?P<from_table>[\w"'`.]+)\s*\.\s*(?P<from_column>[\w"'`]+)\s*
        (?P<relation>[<>-]|<>)\s*
        (?P<to_table>[\w"'`.]+)\s*\.\s*(?P<to_column>[\w"'`]+)\s*$""",
    re.VERBOSE | re.IGNORECASE,
)


def normalize_agent_dbml(dbml: str) -> str:
    """Bỏ các câu `Ref:` lặp lại quan hệ đã khai báo ngay trên cột.

    Args:
        dbml: DBML thô do LLM trả về.

    Returns:
        DBML đã bỏ dòng `Ref:` thừa; trả nguyên bản khi không parse được hoặc không có gì
        để bỏ, để bước kiểm định phía sau báo lỗi cú pháp như bình thường.
    """
    try:
        diagram = loads(dbml)
    except UnexpectedInput:
        return dbml

    # Bắt đầu từ các quan hệ khai báo trên cột, rồi bồi thêm từng câu `Ref:` gặp được —
    # nhờ vậy dedupe được cả trường hợp hai câu `Ref:` giống hệt nhau mà không có inline.
    declared = _inline_endpoints(diagram)

    kept, removed = _deduplicate_ref_lines(dbml, declared)
    if removed == 0:
        return dbml
    logger.info("dbml_duplicate_refs_removed count=%d", removed)
    return "\n".join(kept)


def _deduplicate_ref_lines(
    dbml: str,
    declared: set[frozenset[str]],
) -> tuple[list[str], int]:
    """Loại Ref trùng và trả các dòng còn lại cùng số dòng đã bỏ."""
    kept: list[str] = []
    removed = 0
    for line in dbml.splitlines():
        match = _INLINE_REF_STATEMENT.match(line)
        if match is None:
            kept.append(line)
            continue
        endpoints = _endpoint_key(
            f"{_strip_quotes(match.group('from_table'))}.{_strip_quotes(match.group('from_column'))}",
            f"{_strip_quotes(match.group('to_table'))}.{_strip_quotes(match.group('to_column'))}",
        )
        if endpoints in declared:
            removed += 1
            continue
        declared.add(endpoints)
        kept.append(line)

    return kept, removed


def _inline_endpoints(diagram: object) -> set[frozenset[str]]:
    """Thu thập các quan hệ đã được khai báo ngay trong định nghĩa cột."""
    endpoints: set[frozenset[str]] = set()
    for table in getattr(diagram, "tables", []) or []:
        for column in table.columns or []:
            reference = getattr(getattr(column, "settings", None), "ref", None)
            if reference is None:
                continue
            for to_column in reference.to_columns or []:
                endpoints.add(
                    _endpoint_key(
                        f"{table.name}.{column.name}",
                        f"{reference.to_table.name}.{to_column}",
                    )
                )
    return endpoints


def _endpoint_key(from_endpoint: str, to_endpoint: str) -> frozenset[str]:
    """Khóa nhận dạng một quan hệ, không phân biệt chiều khai báo."""
    return frozenset({from_endpoint, to_endpoint})


def _strip_quotes(identifier: str) -> str:
    """Bỏ dấu nháy bao quanh định danh nếu có."""
    return identifier.strip().strip("\"'`")
