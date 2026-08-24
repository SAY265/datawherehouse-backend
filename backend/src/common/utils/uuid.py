"""Utilities xử lý UUID (uuid.py).

Cung cấp các hàm trợ giúp khởi tạo và kiểm tra tính hợp lệ của UUIDv4.
"""

import uuid
from typing import Any


def generate_uuid() -> uuid.UUID:
    """Sinh ngẫu nhiên một đối tượng UUID (version 4)."""
    return uuid.uuid4()


def generate_uuid_str() -> str:
    """Sinh ngẫu nhiên một chuỗi UUID (version 4) dạng 36 ký tự."""
    return str(uuid.uuid4())


def is_valid_uuid(val: Any) -> bool:
    """Kiểm tra một giá trị có phải là UUID (v4) hợp lệ hay không.

    Hỗ trợ đối tượng uuid.UUID và chuỗi đại diện UUID.
    """
    if isinstance(val, uuid.UUID):
        return True

    if not isinstance(val, str):
        return False

    try:
        parsed = uuid.UUID(val.strip())
        return str(parsed) == val.strip().lower()
    except (ValueError, AttributeError):
        return False
