"""Common DTOs cho các thông tin metadata chung của response."""

from pydantic import BaseModel, Field


class ResponseMeta(BaseModel):
    """Metadata chung đi kèm phản hồi (request_id, timestamp...). Cấm đưa metadata đặc thù LLM/Agent vào đây."""

    request_id: str | None = Field(
        default=None,
        description="Mã định danh request phục vụ truy vết (X-Request-ID)",
    )
    timestamp: str | None = Field(
        default=None,
        description="Thời gian tạo phản hồi (ISO 8601 string)",
    )
