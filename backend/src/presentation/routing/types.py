"""Typed OpenAPI response metadata dùng chung cho Presentation routes."""

from typing import Any, TypeAlias

ErrorResponses: TypeAlias = dict[int | str, dict[str, Any]]

