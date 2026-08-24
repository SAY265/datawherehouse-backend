"""Input models của application service Project."""

from dataclasses import dataclass
from typing import Any

from src.domain.shared.types import EntityID


@dataclass(frozen=True)
class CreateProjectInput:
    """Dữ liệu khởi tạo project và snapshot Data Model đầu tiên."""

    domain: str
    target_dialect: str
    business_description: str
    is_masking_enabled: bool
    source_tables: tuple[dict[str, Any], ...] = ()
    name: str = ""


@dataclass(frozen=True)
class LoadProjectSourceInput:
    """Schema nguồn được nạp sau khi project đã tồn tại."""

    project_id: EntityID
    target_dialect: str
    is_masking_enabled: bool
    source_tables: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class UpdateProjectInput:
    """Dữ liệu cập nhật project."""

    project_id: EntityID
    name: str | None = None
    description: str | None = None
    domain: str | None = None
    status: str | None = None


__all__ = ["CreateProjectInput", "LoadProjectSourceInput", "UpdateProjectInput"]
