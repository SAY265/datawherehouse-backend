"""Interface duy nhất của module Requirement."""

from abc import ABC


class IRequirementService(ABC):
    """Hợp đồng application cho các use case Requirement.

    Module chưa có use case được hiện thực; method mới phải được thêm tại đây.
    """
