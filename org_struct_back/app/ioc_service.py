import functools
from collections.abc import Callable
from typing import Any

from fastapi import Depends, Request


def Inject[T](t: T) -> Any:  # noqa: N802
    def resolver(t: T, request: Request) -> Callable[..., T]:
        return request.app.state.ioc_container.resolve(t)  # type: ignore[no-any-return]

    return Depends(functools.partial(resolver, t))
