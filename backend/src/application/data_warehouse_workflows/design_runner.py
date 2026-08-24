"""Điều phối validation retry quanh từng invocation của DWDesignAgent."""

from dataclasses import replace

from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataModelValidationEngine,
    IDataWarehouseDesignAgent,
)
from src.application.data_warehouse_workflows.input import (
    ConversationDesignInput,
    DataWarehouseDesignInput,
    RevisionDesignInput,
)
from src.application.data_warehouse_workflows.output import (
    ConversationDesignResult,
    GeneratedDbml,
    ValidationIssue,
    ValidationSeverity,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode

MAX_DESIGN_ATTEMPTS = 3


class WorkflowDesignRunner:
    """Gọi một LLM invocation mỗi attempt và retry tối đa ba lần."""

    def __init__(
        self, design_agent: IDataWarehouseDesignAgent,
        validator: IDataModelValidationEngine,
    ) -> None:
        self._design_agent = design_agent
        self._validator = validator

    async def generate(self, data: DataWarehouseDesignInput) -> GeneratedDbml:
        """Sinh DBML ban đầu và truyền lỗi validation sang attempt kế tiếp."""
        previous: str | None = None
        issues: tuple[ValidationIssue, ...] = ()
        for _ in range(MAX_DESIGN_ATTEMPTS):
            invocation = replace(data, failed_dbml=previous, validation_issues=issues)
            result = await self._design_agent.generate(invocation)
            issues = self._error_issues(result.dbml)
            if not issues:
                return result
            previous = result.dbml
        self._raise_exhausted()

    async def revise(self, data: RevisionDesignInput) -> GeneratedDbml:
        """Chỉnh DBML và retry bằng cách đưa bản nháp vừa sinh kèm validation issues."""
        current_dbml = data.current_dbml
        issues = data.validation_issues
        for _ in range(MAX_DESIGN_ATTEMPTS):
            invocation = replace(data, current_dbml=current_dbml, validation_issues=issues)
            result = await self._design_agent.revise(invocation)
            issues = self._error_issues(result.dbml)
            if not issues:
                return result

            # Lần retry tiếp theo sẽ sửa trên chính bản DBML vừa sinh
            current_dbml = result.dbml
        self._raise_exhausted()

    async def converse(self, data: ConversationDesignInput) -> ConversationDesignResult:
        """Thực hiện một lượt hội thoại thiết kế kho dữ liệu với DWDesignAgent."""
        return await self._design_agent.converse(data)

    def _error_issues(self, dbml: str) -> tuple[ValidationIssue, ...]:
        """Chỉ lấy typed issue severity ERROR làm điều kiện retry."""
        return tuple(
            item for item in self._validator.validate(dbml)
            if item.severity is ValidationSeverity.ERROR
        )

    @staticmethod
    def _raise_exhausted() -> None:
        """Báo lỗi nghiệp vụ sau đúng ba attempt không hợp lệ."""
        raise BusinessException(
            ErrorCode.DATA_MODEL_AGENT_VALIDATION_RETRIES_EXHAUSTED,
            "DWDesignAgent không tạo được DBML hợp lệ sau 3 lần thử.",
        )
