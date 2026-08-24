"""Port sinh artifact từ snapshot DBML hiện tại."""

from abc import ABC, abstractmethod

from src.application.data_models.output import DataModelInsightOutput


class IDataModelArtifactGenerator(ABC):
    """Hợp đồng codegen và phân tích không phụ thuộc thư viện parser cụ thể."""

    @abstractmethod
    def generate_ddl(self, dbml: str, dialect: str) -> str:
        """Sinh DDL theo dialect từ DBML hợp lệ."""
        raise NotImplementedError

    @abstractmethod
    def analyze(self, dbml: str) -> list[DataModelInsightOutput]:
        """Phân tích cấu trúc Data Model thành insight hiển thị cho người dùng."""
        raise NotImplementedError
