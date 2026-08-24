"""Interface duy nhất của module Session."""

from abc import ABC


class ISessionService(ABC):
    """Hợp đồng application cho các use case Session.

    Module chưa có use case được hiện thực; method mới phải được thêm tại đây.
    """
