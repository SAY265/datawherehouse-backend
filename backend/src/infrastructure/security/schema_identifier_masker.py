"""Che định danh DBML nhạy cảm bằng placeholder có thể hoàn nguyên."""

import re
from dataclasses import dataclass, field

from src.common.logging import get_logger
from src.infrastructure.security.schema_identifier_patterns import (
    COLUMN_LINE_REGEX,
    IDENTIFIER_REGEX,
    NON_COLUMN_LINE_KEYWORDS,
    PLACEHOLDER_TEMPLATE,
    RESIDUAL_PLACEHOLDER_REGEX,
    SENSITIVE_COLUMN_KEYWORDS,
)

logger = get_logger(__name__)


@dataclass(frozen=True)
class MaskedPayload:
    """Văn bản đã che cùng mapping chỉ sống trong một lời gọi."""

    text: str
    mapping: dict[str, str] = field(default_factory=dict)

    @property
    def masked_count(self) -> int:
        """Trả số định danh đã được che."""
        return len(self.mapping)


class SchemaIdentifierMasker:
    """Che tên cột nhạy cảm mà vẫn bảo toàn khả năng hoàn nguyên DBML."""

    def mask_schema(self, dbml: str) -> MaskedPayload:
        """Che tên cột nhạy cảm trong khai báo DBML."""
        return self._apply_placeholders(dbml, _collect_sensitive_columns(dbml))

    def mask_identifiers(self, text: str) -> MaskedPayload:
        """Che định danh nhạy cảm ở mọi vị trí trong văn bản."""
        originals = list(
            dict.fromkeys(
                token for token in IDENTIFIER_REGEX.findall(text) if _is_sensitive(token)
            )
        )
        return self._apply_placeholders(text, originals)

    def unmask(self, text: str, mapping: dict[str, str]) -> str:
        """Hoàn nguyên chính xác placeholder từ mapping của lời gọi."""
        restored = text
        for placeholder, original in mapping.items():
            restored = re.sub(rf"\b{re.escape(placeholder)}\b", original, restored)
        return restored

    def has_residual_placeholder(self, text: str) -> bool:
        """Phát hiện placeholder bị LLM làm biến dạng nên chưa hoàn nguyên."""
        return bool(text and RESIDUAL_PLACEHOLDER_REGEX.search(text))

    @staticmethod
    def _apply_placeholders(text: str, originals: list[str]) -> MaskedPayload:
        """Che danh sách định danh và tạo mapping ngược trong bộ nhớ."""
        replacements = _build_replacements(originals)
        masked = text
        for original, placeholder in replacements.items():
            masked = re.sub(rf"\b{re.escape(original)}\b", placeholder, masked)
        mapping = {placeholder: original for original, placeholder in replacements.items()}
        if mapping:
            logger.info("pii_schema_masked fields=%d", len(mapping))
        return MaskedPayload(masked, mapping)


def _build_replacements(originals: list[str]) -> dict[str, str]:
    """Tạo placeholder ổn định theo thứ tự định danh xuất hiện."""
    return {
        name: PLACEHOLDER_TEMPLATE.format(index=index)
        for index, name in enumerate(originals, start=1)
    }


def _collect_sensitive_columns(dbml: str) -> list[str]:
    """Thu thập tên cột DBML nhạy cảm, giữ thứ tự xuất hiện."""
    names: list[str] = []
    for line in dbml.splitlines():
        match = COLUMN_LINE_REGEX.match(line)
        name = match.group("name") if match else ""
        if name.lower() in NON_COLUMN_LINE_KEYWORDS or not _is_sensitive(name):
            continue
        if name not in names:
            names.append(name)
    return names


def _is_sensitive(column_name: str) -> bool:
    """Kiểm tra tên cột có chứa từ khóa PII."""
    lowered = column_name.lower()
    return any(keyword in lowered for keyword in SENSITIVE_COLUMN_KEYWORDS)
