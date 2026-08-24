"""Interface duy nhất của module Workflow."""

from abc import ABC


class IWorkflowService(ABC):
    """Hợp đồng application cho các use case Workflow.

    Module chưa có use case được hiện thực; method mới phải được thêm tại đây.
    """
