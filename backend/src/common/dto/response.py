"""Common Generic API Response Envelope DTO theo chuẩn TECHNICAL_CODING_GUIDELINES.md (Status 200 OK)."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from src.common.dto.metadata import ResponseMeta

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Khung phản hồi thành công chuẩn cho toàn bộ hệ thống API.

    Tuân theo chuẩn Section III.3 của TECHNICAL_CODING_GUIDELINES.md:
    {
        "status": "success",
        "code": 200,
        "message": "Xử lý thành công",
        "data": ...,
        "meta": ... (optional)
    }
    """

    status: str = Field(
        default="success",
        description="Trạng thái phản hồi (luôn là 'success' đối với 2xx)",
    )
    code: int = Field(
        default=200,
        description="HTTP Status Code (mặc định 200)",
    )
    message: str = Field(
        default="Xử lý thành công",
        description="Thông điệp phản hồi cho người dùng",
    )
    data: T | None = Field(
        default=None,
        description="Dữ liệu payload chính trả về",
    )
    meta: ResponseMeta | None = Field(
        default=None,
        description="Metadata chung đi kèm phản hồi (request_id, timestamp... nếu có)",
    )
