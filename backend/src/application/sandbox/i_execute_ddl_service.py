"""Interface cho Service Thực thi DDL Sandbox (UC9.2)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.application.sandbox.dto import ExecuteDdlRequest, ExecuteDdlResponse


class IExecuteDdlService(ABC):
    """Interface định nghĩa hợp đồng chạy thử DDL script trên Sandbox DB."""

    @abstractmethod
    async def execute_ddl(self, project_id: UUID, request: ExecuteDdlRequest) -> ExecuteDdlResponse:
        """Thực thi mã DDL script lên Sandbox Database đã được cấu hình của dự án."""
        pass
