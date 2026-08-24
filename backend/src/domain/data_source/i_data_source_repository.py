"""Giao diện repository cho DataSource."""

from abc import abstractmethod

from src.domain.data_source.entities import DataSource
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IDataSourceRepository(IBaseRepository[DataSource]):
    """Định nghĩa persistence dành cho nguồn dữ liệu."""

    @abstractmethod
    async def list_by_project(self, project_id: EntityID) -> list[DataSource]:
        """Lấy danh sách nguồn dữ liệu của dự án.

        Args:
            project_id: Định danh dự án.

        Returns:
            Danh sách nguồn dữ liệu của dự án.
        """

    @abstractmethod
    async def count_by_project_ids(
        self,
        project_ids: tuple[EntityID, ...],
    ) -> dict[EntityID, int]:
        """Đếm nguồn dữ liệu theo từng dự án mà không tải entity.

        Args:
            project_ids: Các định danh dự án cần thống kê.

        Returns:
            Ánh xạ định danh dự án sang số nguồn dữ liệu.
        """
