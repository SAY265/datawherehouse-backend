"""Lớp thực thể cơ sở (BaseEntity) cho toàn bộ domain."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.common.utils.datetime import ensure_utc, utc_now
from src.domain.shared.types import EntityID


@dataclass(eq=False)
class BaseEntity:
    """Lớp cơ sở cho các Entity trong tầng Domain.

    Quản lý id (UUIDv4) và các mốc thời gian created_at, updated_at chuẩn UTC.
    Equality và Hash hoàn toàn dựa vào identity `id`.
    """

    id: EntityID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Đảm bảo các trường datetime luôn có timezone UTC."""
        self.created_at = ensure_utc(self.created_at)
        self.updated_at = ensure_utc(self.updated_at)

    def mark_updated(self) -> None:
        """Cập nhật mốc thời gian updated_at thành thời gian hiện tại chuẩn UTC."""
        self.updated_at = utc_now()

    def __eq__(self, other: object) -> bool:
        """So sánh hai Entity dựa trên identity `id`."""
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Mã băm dựa trên identity `id`."""
        return hash(self.id)
