"""Lớp cơ sở và cơ chế Composition cho Interceptor (base.py).

Định nghĩa BaseInterceptor, InterceptorChain và decorator @intercepted.
"""

import functools
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from src.common.interceptors.context import InterceptorContext

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


class BaseInterceptor(ABC):
    """Lớp trừu tượng định nghĩa hợp đồng Interceptor."""

    @abstractmethod
    async def intercept(
        self,
        context: InterceptorContext,
        call_next: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Thực thi logic bao quanh operation.

        Phải gọi `await call_next()` để tiếp tục chuỗi thực thi.
        """
        ...


class InterceptorChain:
    """Quản lý và phối hợp danh sách nhiều Interceptors theo chuỗi lồng nhau."""

    def __init__(self, interceptors: list[BaseInterceptor] | None = None) -> None:
        self._interceptors: list[BaseInterceptor] = interceptors or []

    def add_interceptor(self, interceptor: BaseInterceptor) -> "InterceptorChain":
        """Thêm một interceptor vào cuối chuỗi."""
        self._interceptors.append(interceptor)
        return self

    async def execute(
        self,
        context: InterceptorContext,
        target: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Thực thi target operation qua tất cả các interceptors theo thứ tự."""
        if not self._interceptors:
            return await target()

        async def dispatch(current_index: int) -> Any:
            if current_index >= len(self._interceptors):
                return await target()

            interceptor = self._interceptors[current_index]
            return await interceptor.intercept(
                context,
                lambda: dispatch(current_index + 1),
            )

        return await dispatch(0)


def intercepted(
    *interceptors: BaseInterceptor,
    operation_name: str | None = None,
) -> Callable[[F], F]:
    """Decorator bao quanh async function / use-case method bằng chuỗi Interceptor."""
    chain = InterceptorChain(list(interceptors))

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            name = operation_name or func.__name__
            context = InterceptorContext.create(name)
            return await chain.execute(context, lambda: func(*args, **kwargs))

        return wrapper  # type: ignore[return-value]

    return decorator
