"""Common DTOs cho xử lý sắp xếp (Sorting)."""

from enum import StrEnum

from pydantic import BaseModel, Field


class SortOrder(StrEnum):
    """Thứ tự sắp xếp dữ liệu (tăng dần hoặc giảm dần)."""

    ASC = "asc"
    DESC = "desc"


class SortRequest(BaseModel):
    """DTO chứa tham số yêu cầu sắp xếp từ client (sort_by, sort_order)."""

    sort_by: str | None = Field(
        default=None,
        description="Tên trường cần sắp xếp (ví dụ: created_at, name). Null nếu không sắp xếp.",
    )
    sort_order: SortOrder = Field(
        default=SortOrder.DESC,
        description="Thứ tự sắp xếp ('asc' hoặc 'desc')",
    )
