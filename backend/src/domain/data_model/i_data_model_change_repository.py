"""Giao diện repository cho DataModelChange."""

from abc import abstractmethod

from src.domain.data_model.entities import DataModelChange
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IDataModelChangeRepository(IBaseRepository[DataModelChange]):
    """Định nghĩa persistence dành cho đề xuất thay đổi mô hình."""

    @abstractmethod
    async def get_proposed_by_data_model_and_user(
        self,
        data_model_id: EntityID,
        user_id: EntityID,
    ) -> DataModelChange | None:
        """Lấy đề xuất đang chờ của một người dùng trên một Data Model.

        Args:
            data_model_id: Định danh mô hình dữ liệu.
            user_id: Định danh người tạo đề xuất.

        Returns:
            Đề xuất ``PROPOSED`` hiện có hoặc ``None``.
        """
