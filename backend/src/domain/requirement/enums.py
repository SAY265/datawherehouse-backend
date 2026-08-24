"""Các kiểu liệt kê (Enums) thuộc miền Yêu cầu (Requirement)."""

from enum import StrEnum


class RequirementType(StrEnum):
    """Phân loại Yêu cầu (Requirement Type)."""

    BUSINESS = "BUSINESS"
    ANALYTICAL = "ANALYTICAL"
    TECHNICAL = "TECHNICAL"


class RequirementPriority(StrEnum):
    """Mức độ ưu tiên của Yêu cầu (Requirement Priority)."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
