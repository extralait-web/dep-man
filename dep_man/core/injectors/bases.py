"""Base injector module."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any, cast, overload

from typing_extensions import Self

from dep_man.core.exceptions import ClassBaseInjectionContextDoesNotSupport
from dep_man.core.mocker import mock_provider

from .interfaces import IInjector

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from dep_man.types import P, PExecutor, ProvidersType, R, T
    from dep_man.utils.contextvar import SimpleContext


class Injector(IInjector):
    """Dependency injector."""

    __exit: Callable | None = None
    """SimpleContextManager __exit__ function"""
    _providers: dict[str, type | Callable[[Any, Any, Any], Any]] | None
    """Injector providers from passed scopes"""

    def __init__(
        self,
        providers: dict[str, Callable | type] | None,
        *,
        __executor__: PExecutor,
        __context__: SimpleContext[ProvidersType],
    ):
        """Set current providers.

        Args:
            providers: providers dict
            __executor__: provider executor
            __context__: dependency manager context
        """
        self._providers = providers
        self.__executor__ = __executor__
        self.__context__ = __context__

    @overload
    def __call__(self, target: type[T]) -> type[T]: ...
    @overload
    def __call__(self, target: Callable[P, R]) -> Callable[P, R]: ...
    def __call__(self, target: Callable[P, R] | type[T]) -> Callable[P, R] | type[T]:
        """Call function for using injector as decorator."""
        mock_provider(target, self.__executor__)

        if isinstance(target, type):
            if self._providers is not None:
                raise ClassBaseInjectionContextDoesNotSupport(name=target.__name__)

            return target

        if inspect.iscoroutinefunction(target):
            # wrapper for async function
            @wraps(target)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Awaitable[R]:  # pyright: ignore[reportRedeclaration]
                async with self:
                    return await target(*args, **kwargs)
        else:
            # wrapper for sync function
            @wraps(target)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                with self:
                    return cast("R", target(*args, **kwargs))

        return wrapper  # type:ignore

    def __enter__(self):
        """Enter to context."""
        _current_providers = self.__context__.value
        _providers = {**_current_providers, **(self._providers or {})}
        _manager = self.__context__.manager(_providers)
        _manager.__enter__()
        self.__exit = _manager.__exit__

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit from context."""
        if self.__exit:
            return self.__exit(exc_type, exc_value, traceback)
        return False

    async def __aenter__(self):
        """Enter to context."""
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit from context."""
        return self.__exit__(exc_type, exc_value, traceback)

    @classmethod
    def create(
        cls,
        providers: dict[str, Callable | type] | None,
        *,
        __executor__: PExecutor,
        __context__: SimpleContext[ProvidersType],
    ) -> Self:
        """Create injector instance.

        Args:
            providers: providers dict
            __executor__: provider executor
            __context__: dependency manager context

        Returns: injector instance
        """
        return cls(providers, __executor__=__executor__, __context__=__context__)
