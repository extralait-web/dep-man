"""Starlette integrations tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dep_man.core.managers.utils import request_dependencies_context

if TYPE_CHECKING:
    from dep_man.core.managers.interfaces import IDependencyManager
    from dep_man.types import ScopeNameType


def get_starlette_middleware(
    manager: type[IDependencyManager],
    globalize: bool | tuple[ScopeNameType, ...] = False,
):
    """Return the dependency manager middleware for starlette or fastapi.

    Args:
        manager: DependencyManager object
        globalize: add all or certain scopes providers in global context for using providers without context managers

    Returns: starlette middleware
    """
    from starlette.middleware.base import BaseHTTPMiddleware  # type: ignore

    class DependencyManagerMiddleware(BaseHTTPMiddleware):
        """Dependency manager middleware."""

        async def dispatch(self, request, call_next):
            # init manager context
            manager.init(globalize)
            # return response
            with request_dependencies_context(manager):
                return await call_next(request)

    return DependencyManagerMiddleware
