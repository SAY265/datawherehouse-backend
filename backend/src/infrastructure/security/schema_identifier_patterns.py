"""Pattern chỉ dành cho việc che định danh nhạy cảm trong DBML."""

import re
from typing import Final

SENSITIVE_COLUMN_KEYWORDS: Final = (
    "phone",
    "email",
    "ssn",
    "social_security",
    "credit_card",
    "card_number",
    "address",
    "birth",
    "dob",
    "passport",
    "national_id",
    "cccd",
    "cmnd",
    "tax_code",
    "full_name",
)
PLACEHOLDER_PREFIX: Final = "pii_field_"
PLACEHOLDER_TEMPLATE: Final = PLACEHOLDER_PREFIX + "{index:02d}"
RESIDUAL_PLACEHOLDER_REGEX: Final = re.compile(rf"\b{PLACEHOLDER_PREFIX}\d+\b")
IDENTIFIER_REGEX: Final = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
COLUMN_LINE_REGEX: Final = re.compile(
    r"^(?P<indent>\s+)(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?=\s+\S)"
)
NON_COLUMN_LINE_KEYWORDS: Final = frozenset(
    {"table", "ref", "indexes", "note", "enum", "project", "tablegroup"}
)
