"""Common Utilities Module.

Export minh bạch các hàm tiện ích dùng chung chuẩn Clean Architecture.
"""

from src.common.utils.collections import chunked, is_empty
from src.common.utils.datetime import (
    ensure_utc,
    parse_iso_datetime,
    to_isoformat,
    utc_now,
)
from src.common.utils.json import safe_json_dumps, safe_json_loads
from src.common.utils.string import (
    is_blank,
    normalize_whitespace,
    safe_strip,
    truncate,
)
from src.common.utils.uuid import (
    generate_uuid,
    generate_uuid_str,
    is_valid_uuid,
)

__all__ = [
    "utc_now",
    "ensure_utc",
    "to_isoformat",
    "parse_iso_datetime",
    "generate_uuid",
    "generate_uuid_str",
    "is_valid_uuid",
    "normalize_whitespace",
    "is_blank",
    "truncate",
    "safe_strip",
    "safe_json_dumps",
    "safe_json_loads",
    "chunked",
    "is_empty",
]
