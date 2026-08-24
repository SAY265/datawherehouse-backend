"""Interface duy nhất của module Data Source."""

from abc import ABC


class IDataSourceService(ABC):
    """Hợp đồng application cho các use case Data Source.

    Module chưa có use case được hiện thực; method mới phải được thêm tại đây.
    """
