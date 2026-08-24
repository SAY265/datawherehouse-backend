"""Lớp cơ sở cho Value Object (đối tượng giá trị bất biến)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BaseValueObject:
    """Lớp cơ sở bất biến (immutable) cho các Value Object trong domain."""

    pass
