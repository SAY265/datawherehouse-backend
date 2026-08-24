"""Các kiểu liệt kê (Enums) thuộc miền Phiên Agent (Agent Session)."""

from enum import StrEnum


class SessionStatus(StrEnum):
    """Trạng thái phiên làm việc (Project Session Status)."""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class SessionEventRole(StrEnum):
    """Vai trò khởi tạo sự kiện trong phiên."""

    USER = "USER"
    AGENT = "AGENT"
    TOOL = "TOOL"


class SessionEventType(StrEnum):
    """Loại sự kiện diễn ra trong phiên."""

    MESSAGE = "MESSAGE"
    QUESTION = "QUESTION"
    ANSWER = "ANSWER"
    AGENT_CALL = "AGENT_CALL"
    AGENT_RESULT = "AGENT_RESULT"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"


class AgentType(StrEnum):
    """Danh sách 4 Agent hợp lệ trong hệ thống."""

    ORCHESTRATOR = "OrchestratorAgent"
    REQUIREMENT = "RequirementAgent"
    DATA_SOURCE = "DataSourceAgent"
    DW_DESIGN = "DWDesignAgent"


class AgentResultStatus(StrEnum):
    """Trạng thái kết quả thực thi của Agent (SUCCESS, FAILED, CANCELLED)."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ToolResultStatus(StrEnum):
    """Trạng thái kết quả thực thi của Tool (SUCCESS, FAILED)."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
