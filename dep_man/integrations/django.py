"""Django integrations tools."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dep_man.core.managers.interfaces import IDependencyManager
    from dep_man.types import ScopeNameType


def get_django_middleware(
    manager: type[IDependencyManager],
    globalize: bool | tuple[ScopeNameType] = False,
):
    """Return the dependency manager middleware for django.

    Args:
        manager: DependencyManager object
        globalize: add all or certain scopes providers in global context for using providers without context managers

    Returns: django middleware
    """
    from django.utils.decorators import sync_and_async_middleware  # type: ignore

    @sync_and_async_middleware  # type: ignore
    def dependency_manager_middleware(get_response):
        """Dependency manager middleware."""
        if inspect.iscoroutinefunction(get_response):
            # async view middleware
            async def middleware(request):  # pyright: ignore [reportRedeclaration]
                # init manager context
                manager.init(globalize)
                # return response
                return await get_response(request)

        else:
            # sync view middleware
            def middleware(request):
                # init manager context
                manager.init(globalize)
                # return response
                return get_response(request)

        return middleware

    return dependency_manager_middleware
