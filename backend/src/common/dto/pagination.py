"""Common DTOs cho xử lý phân trang (Pagination)."""

import math
from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from src.common.constants.pagination import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)

T = TypeVar("T")


class PaginationRequest(BaseModel):
    """DTO biểu diễn các tham số phân trang gửi từ client trong query string (?page=1&page_size=20)."""

    page: int = Field(
        default=DEFAULT_PAGE,
        ge=1,
        description="Số trang cần lấy (bắt đầu từ 1)",
    )
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"Số lượng bản ghi trên một trang (tối đa {MAX_PAGE_SIZE})",
    )


class PaginationMeta(BaseModel):
    """DTO chứa thông tin metadata của phân trang trả về cho client."""

    page: int = Field(..., ge=1, description="Số trang hiện tại")
    page_size: int = Field(..., ge=1, description="Kích thước trang")
    total_items: int = Field(..., ge=0, description="Tổng số bản ghi")
    total_pages: int = Field(..., ge=0, description="Tổng số trang")

    @classmethod
    def create(cls, page: int, page_size: int, total_items: int) -> "PaginationMeta":
        """Factory method hỗ trợ tính toán total_pages tự động từ total_items và page_size."""
        total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic DTO biểu diễn dữ liệu danh sách đã phân trang kèm metadata."""

    data: list[T] = Field(default_factory=list, description="Danh sách các phần tử của trang")
    meta: PaginationMeta = Field(..., description="Thông tin metadata phân trang")
