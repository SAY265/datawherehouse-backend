"""Interface duy nhất cho các thao tác application Data Model."""

from abc import ABC, abstractmethod

from src.application.data_models.input import (
    GetDataModelInput,
    RunRelationshipAgentInput,
    UpdateDataModelInput,
)
from src.application.data_models.output import (
    DataModelDdlOutput,
    DataModelInsightOutput,
    DataModelOutput,
    RelationshipAgentOutput,
)


class IDataModelService(ABC):
    """Hợp đồng công khai của application service Data Model."""

    @abstractmethod
    async def get_data_model(self, data: GetDataModelInput) -> DataModelOutput:
        """Lấy Data Model hiện tại của dự án."""
        raise NotImplementedError

    @abstractmethod
    async def update_data_model(self, data: UpdateDataModelInput) -> DataModelOutput:
        """Cập nhật Data Model bằng optimistic locking."""
        raise NotImplementedError

    @abstractmethod
    async def generate_ddl(self, data: GetDataModelInput, dialect: str) -> DataModelDdlOutput:
        """Sinh DDL từ snapshot hiện tại."""
        raise NotImplementedError

    @abstractmethod
    async def get_insights(self, data: GetDataModelInput) -> list[DataModelInsightOutput]:
        """Lấy insight được phân tích từ snapshot hiện tại."""
        raise NotImplementedError

    @abstractmethod
    async def run_relationship_agent(
        self, data: RunRelationshipAgentInput
    ) -> RelationshipAgentOutput:
        """Tự nối quan hệ trên bản nháp DBML sau khi kiểm tra quyền project."""
        raise NotImplementedError
