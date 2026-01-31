"""Injector interface module."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, overload

from typing_extensions import Self

if TYPE_CHECKING:
    from collections.abc import Callable

    from dep_man.types import P, PExecutor, ProvidersType, R
    from dep_man.utils.contextvar import SimpleContext


class IInjector(ABC):
    """Dependency injector interface."""

    __executor__: PExecutor
    """Provider executor"""
    __context__: SimpleContext[ProvidersType]
    """Dependency manager context"""

    @overload
    @abstractmethod
    def __call__(self, target: type) -> type: ...
    @overload
    @abstractmethod
    def __call__(self, target: Callable[P, R]) -> Callable[P, R]: ...
    @abstractmethod
    def __call__(self, target: Callable[P, R] | type) -> Callable[P, R] | type:
        """Call function for using injector as decorator."""

    @abstractmethod
    def __enter__(self):
        """Enter to context."""

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback) -> Any:
        """Exit from context."""

    @abstractmethod
    async def __aenter__(self):
        """Enter to async context."""

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> Any:
        """Exit from async context."""

    @classmethod
    @abstractmethod
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
