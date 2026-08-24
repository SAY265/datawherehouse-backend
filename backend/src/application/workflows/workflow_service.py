"""Application service duy nhất của module Workflow."""

from src.application.workflows.i_workflow_service import IWorkflowService


class WorkflowService(IWorkflowService):
    """Điểm hiện thực tập trung cho các use case Workflow."""
