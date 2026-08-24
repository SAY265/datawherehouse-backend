"""Interceptor đo thời gian thực thi Application Operation (timing.py).

Sử dụng time.perf_counter() để đo độ trễ thực thi chính xác theo ms.
"""

import time
from collections.abc import Awaitable, Callable
from typing import Any

from src.common.interceptors.base import BaseInterceptor
from src.common.interceptors.context import InterceptorContext


class TimingInterceptor(BaseInterceptor):
    """Interceptor đo thời gian thực thi của operation."""

    async def intercept(
        self,
        context: InterceptorContext,
        call_next: Callable[[], Awaitable[Any]],
    ) -> Any:
        start_time = time.perf_counter()
        try:
            return await call_next()
        finally:
            elapsed = time.perf_counter() - start_time
            duration_ms = round(elapsed * 1000, 2)
            context.metadata["duration_ms"] = duration_ms
