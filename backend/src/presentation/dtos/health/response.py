"""Response payload cho các endpoints Health Check (Liveness, Readiness, Deep Health)."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ComponentHealth(BaseModel):
    """Trạng thái chi tiết của từng thành phần phụ thuộc."""

    model_config = ConfigDict(extra="ignore")

    status: str = Field(description="Trạng thái của thành phần (healthy, degraded, unhealthy)")
    message: str | None = Field(default=None, description="Thông tin chi tiết hoặc lỗi nếu có")
    latency_ms: float | None = Field(default=None, description="Thời gian phản hồi tính bằng mili-giây")


class HealthResponse(BaseModel):
    """Trạng thái tổng hợp hoạt động và môi trường hiện tại của Backend."""

    model_config = ConfigDict(extra="ignore")

    status: str = Field(default="ok", description="Trạng thái hoạt động chung (ok, degraded, unhealthy)")
    env: str = Field(description="Môi trường chạy hiện tại (development, production, test)")
    timestamp: str | None = Field(default=None, description="Thời điểm kiểm tra (ISO 8601 UTC)")
    version: str = Field(default="1.0.0", description="Phiên bản API hiện tại")
    components: dict[str, Any] | None = Field(default=None, description="Trạng thái chi tiết các dịch vụ phụ thuộc")


class LivenessResponse(BaseModel):
    """Payload phản hồi cho Liveness probe (kiểm tra tiến trình server còn sống)."""

    model_config = ConfigDict(extra="ignore")

    status: str = Field(default="ok", description="Trạng thái sống của tiến trình FastAPI")
    timestamp: str = Field(description="Thời điểm kiểm tra")


class ReadinessResponse(BaseModel):
    """Payload phản hồi cho Readiness probe (kiểm tra khả năng sẵn sàng phục vụ)."""

    model_config = ConfigDict(extra="ignore")

    status: str = Field(description="Trạng thái sẵn sàng (ready, not_ready)")
    components: dict[str, Any] = Field(description="Kết quả kiểm tra chi tiết các thành phần")
    timestamp: str = Field(description="Thời điểm kiểm tra")
