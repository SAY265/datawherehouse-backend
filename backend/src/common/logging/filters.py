"""Log Filters cho việc bổ sung ContextVars và ẩn thông tin nhạy cảm (Sensitive Data Redaction)."""

import logging
import re
from typing import Any

from src.common.logging.context import (
    get_agent_name,
    get_correlation_id,
    get_request_id,
    get_session_id,
)

SENSITIVE_PATTERNS = [
    r"password",
    r"password_hash",
    r"access_token",
    r"refresh_token",
    r"api_key",
    r"secret",
    r"client_secret",
    r"authorization",
    r"jwt",
    r"bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*",
]

SENSITIVE_REGEX = re.compile("|".join(SENSITIVE_PATTERNS), re.IGNORECASE)
REDACTED_STR = "***REDACTED***"


class ContextLogFilter(logging.Filter):
    """Filter tự động gắn thông tin ngữ cảnh (request_id, correlation_id, session_id, agent_name) vào từng LogRecord."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(record, "request_id", None) or get_request_id() or "-"
        record.correlation_id = getattr(record, "correlation_id", None) or get_correlation_id() or "-"
        record.session_id = getattr(record, "session_id", None) or get_session_id() or "-"
        record.agent_name = getattr(record, "agent_name", None) or get_agent_name() or "-"
        return True


class SensitiveDataFilter(logging.Filter):
    """Filter quét và ẩn thông tin nhạy cảm (tokens, passwords, api keys) trong log output."""

    def redact_val(self, val: Any) -> Any:
        if isinstance(val, str):
            # Nếu string chứa thông tin nhạy cảm dạng key=val hoặc Bearer token
            if SENSITIVE_REGEX.search(val):
                # Mask chuỗi bearer token nếu có
                val = re.sub(
                    r"(Bearer\s+)[a-zA-Z0-9\-\._~\+\/]+=*",
                    r"\1" + REDACTED_STR,
                    val,
                    flags=re.IGNORECASE,
                )
        elif isinstance(val, dict):
            return {k: REDACTED_STR if SENSITIVE_REGEX.search(str(k)) else self.redact_val(v) for k, v in val.items()}
        elif isinstance(val, list | tuple):
            return [self.redact_val(item) for item in val]
        return val

    def filter(self, record: logging.LogRecord) -> bool:
        # Redact message string
        if isinstance(record.msg, str) and SENSITIVE_REGEX.search(record.msg):
            # Check key-value assignments in message
            record.msg = re.sub(
                r"(password|access_token|refresh_token|api_key|secret|authorization)\s*=\s*['\"][^'\"]+['\"]",
                r"\1='" + REDACTED_STR + "'",
                record.msg,
                flags=re.IGNORECASE,
            )
            record.msg = re.sub(
                r"(Bearer\s+)[a-zA-Z0-9\-\._~\+\/]+=*",
                r"\1" + REDACTED_STR,
                record.msg,
                flags=re.IGNORECASE,
            )

        # Redact record args if present
        if record.args:
            if isinstance(record.args, dict):
                record.args = self.redact_val(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(self.redact_val(a) for a in record.args)

        return True
