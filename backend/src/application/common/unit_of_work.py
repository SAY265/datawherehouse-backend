"""Giao diện transaction cho các application use case."""

from abc import ABC, abstractmethod


class IUnitOfWork(ABC):
    """Điều phối commit/rollback mà không phụ thuộc SQLAlchemy."""

    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction hiện tại."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction hiện tại."""
        pass
