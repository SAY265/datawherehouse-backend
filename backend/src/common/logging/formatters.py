"""Formatters cho cấu hình hiển thị log ở môi trường Console (Dev) và JSON (Prod)."""

import json
import logging
from datetime import UTC, datetime


class ConsoleFormatter(logging.Formatter):
    """Formatter định dạng dễ đọc cho môi trường Development trên terminal."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=UTC).strftime("%Y-%m-%d %H:%M:%S")
        request_id = getattr(record, "request_id", "-")
        agent_name = getattr(record, "agent_name", "-")

        context_str = f" [req_id={request_id}]" if request_id != "-" else ""
        if agent_name != "-":
            context_str += f" [agent={agent_name}]"

        log_fmt = f"{timestamp} | {record.levelname:<8} | {record.name} | {record.getMessage()}{context_str}"

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
            log_fmt += f"\n{record.exc_text}"

        return log_fmt


class JsonFormatter(logging.Formatter):
    """Formatter xuất ra định dạng JSON cấu trúc (Structured Logging) cho môi trường Production."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, str | int | float | None] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "correlation_id": getattr(record, "correlation_id", None),
            "session_id": getattr(record, "session_id", None),
            "agent_name": getattr(record, "agent_name", None),
        }

        # Loại bỏ các giá trị None hoặc "-" để JSON gọn gàng
        log_obj = {k: v for k, v in log_obj.items() if v not in (None, "-")}

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
            log_obj["exception"] = record.exc_text

        return json.dumps(log_obj, ensure_ascii=False)
