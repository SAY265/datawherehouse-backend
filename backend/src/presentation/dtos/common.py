"""DTO phản hồi lỗi dùng chung tại HTTP presentation boundary."""

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    """Chi tiết validation của một trường request."""

    model_config = ConfigDict(extra="forbid")

    field: str = Field(description="Đường dẫn field không hợp lệ")
    message: str = Field(description="Mô tả lỗi validation")


class ApiErrorResponse(BaseModel):
    """Error envelope được Global Exception Handler trả về."""

    model_config = ConfigDict(extra="forbid")

    code: int = Field(ge=400, le=599, description="HTTP status code")
    message: str = Field(description="Thông báo lỗi")
    error_code: str = Field(description="Mã lỗi ổn định cho client")
    details: list[ErrorDetail] | None = Field(
        default=None,
        description="Danh sách chi tiết lỗi theo field",
    )
