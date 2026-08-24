"""Utilities xử lý tập hợp / collections (collections.py).

Cung cấp các hàm generic xử lý iterable, list, set, dictionary.
"""

from collections.abc import Collection, Iterable
from typing import Any, TypeVar

T = TypeVar("T")


def chunked(iterable: Iterable[T], size: int) -> list[list[T]]:
    """Chia một iterable thành các danh sách con (chunk) có độ dài tối đa size.

    Ném ValueError nếu size nhỏ hơn 1.
    """
    if size < 1:
        raise ValueError("Kích thước chunk (size) phải lớn hơn hoặc bằng 1.")

    items = list(iterable)
    return [items[i : i + size] for i in range(0, len(items), size)]


def is_empty(collection: Collection[Any] | None) -> bool:
    """Kiểm tra một collection là None hoặc có số lượng phần tử bằng 0."""
    if collection is None:
        return True
    return len(collection) == 0
