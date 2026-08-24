"""Các kiểu liệt kê (Enums) thuộc miền Yêu cầu Phân tích (Analytical Requirement)."""

from enum import StrEnum


class AggregationMethod(StrEnum):
    """Phương thức tổng hợp dữ liệu (SUM, AVG, COUNT, MAX, MIN...)."""

    SUM = "SUM"
    AVG = "AVG"
    COUNT = "COUNT"
    COUNT_DISTINCT = "COUNT_DISTINCT"
    MAX = "MAX"
    MIN = "MIN"
