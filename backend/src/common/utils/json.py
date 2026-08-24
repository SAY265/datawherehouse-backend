"""Utilities xử lý JSON (json.py).

Hỗ trợ serialize an toàn cho các kiểu dữ liệu phổ biến:
UUID, datetime, Enum, Decimal, Pydantic BaseModel.
"""

import json
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder xử lý UUID, datetime, Enum, Decimal và Pydantic BaseModel."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, Decimal):
            return float(obj) if obj % 1 != 0 else int(obj)
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode="json")
        return super().default(obj)


def safe_json_dumps(
    obj: Any,
    *,
    ensure_ascii: bool = False,
    indent: int | None = None,
) -> str:
    """Serialize đối tượng Python thành chuỗi JSON an toàn.

    Hỗ trợ UUID, datetime, Enum, Decimal, Pydantic BaseModel.
    Ném TypeError rõ ràng nếu gặp kiểu dữ liệu không hỗ trợ.
    """
    return json.dumps(
        obj,
        cls=CustomJSONEncoder,
        ensure_ascii=ensure_ascii,
        indent=indent,
    )


def safe_json_loads(json_str: str) -> Any:
    """Parse chuỗi JSON thành Python object primitives.

    Ném ValueError nếu chuỗi JSON không đúng định dạng.
    """
    if not isinstance(json_str, str) or not json_str.strip():
        raise ValueError("Chuỗi JSON đầu vào không được rỗng.")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Chuỗi JSON không đúng định dạng: {e}") from e
