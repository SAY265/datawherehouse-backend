"""Utilities xử lý chuỗi văn bản (string.py).

Tuân thủ nguyên tắc:
- Không over-normalize (không tự động lowercase hoặc xóa dấu tiếng Việt/tiếng Nhật trừ khi yêu cầu).
- Pure function, xử lý an toàn với chuỗi rỗng và None.
"""

import re

# Match 1 hoặc nhiều ký tự khoảng trắng
WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_whitespace(value: str) -> str:
    """Loại bỏ khoảng trắng ở 2 đầu và gộp nhiều khoảng trắng liên tiếp thành 1 space."""
    if not isinstance(value, str):
        raise TypeError("Giá trị đầu vào phải là chuỗi (str).")
    return WHITESPACE_PATTERN.sub(" ", value.strip())


def is_blank(value: str | None) -> bool:
    """Kiểm tra chuỗi là None, rỗng ('') hoặc chỉ chứa khoảng trắng."""
    if value is None:
        return True
    return len(value.strip()) == 0


def truncate(value: str, max_length: int, suffix: str = "...") -> str:
    """Cắt ngắn chuỗi nếu vượt quá max_length và gắn suffix ở cuối.

    Ném ValueError nếu max_length nhỏ hơn hoặc bằng độ dài suffix.
    """
    if not isinstance(value, str):
        raise TypeError("Giá trị đầu vào phải là chuỗi (str).")

    if max_length <= len(suffix):
        raise ValueError(f"max_length ({max_length}) phải lớn hơn độ dài suffix ({len(suffix)}).")

    if len(value) <= max_length:
        return value

    return value[: max_length - len(suffix)] + suffix


def safe_strip(value: str | None) -> str | None:
    """Strip khoảng trắng đầu cuối nếu đầu vào là string, giữ nguyên nếu là None."""
    if value is None:
        return None
    return value.strip()
