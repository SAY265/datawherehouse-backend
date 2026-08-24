"""Giao diện repository cho DataModel."""

from abc import abstractmethod

from src.domain.data_model.entities import DataModel
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IDataModelRepository(IBaseRepository[DataModel]):
    """Định nghĩa persistence dành cho mô hình dữ liệu hiện tại."""

    @abstractmethod
    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        """Lấy mô hình dữ liệu theo dự án.

        Args:
            project_id: Định danh dự án.

        Returns:
            Mô hình dữ liệu hiện tại hoặc ``None`` nếu chưa có.
        """

    @abstractmethod
    async def list_by_project_ids(
        self,
        project_ids: tuple[EntityID, ...],
    ) -> dict[EntityID, DataModel]:
        """Lấy Data Model theo nhiều dự án bằng một lần đọc.

        Args:
            project_ids: Các định danh dự án cần tải.

        Returns:
            Ánh xạ project ID sang Data Model hiện hữu.
        """

    @abstractmethod
    async def update_if_revision_matches(
        self,
        entity: DataModel,
        base_revision: int,
    ) -> DataModel | None:
        """Cập nhật entity nếu revision trong persistence vẫn khớp.

        Args:
            entity: Mô hình đã được Domain tăng revision.
            base_revision: Revision kỳ vọng trong persistence.

        Returns:
            Entity đã lưu hoặc ``None`` khi có optimistic conflict.
        """
