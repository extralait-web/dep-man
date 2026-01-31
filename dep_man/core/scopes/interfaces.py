"""Bases scope class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, overload

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import MappingProxyType

    from typing_extensions import Self

    from dep_man.types import P, PExecutor, ProvidersType, R, ScopeNameType, T


class IScope(ABC):
    """Class for scope management."""

    __executor__: PExecutor
    """Provider executor."""
    __resolve_cache__: ProvidersType | None
    """Provider cache."""

    name: ScopeNameType
    """Scope name"""
    include: tuple[ScopeNameType, ...]
    """External scopes names for include dependencies in current scope"""

    @classmethod
    @abstractmethod
    def create(
        cls,
        name: ScopeNameType,
        include: tuple[ScopeNameType, ...] = (),
        *,
        __executor__: PExecutor,
        **_kwargs: Any,
    ) -> Self:
        """Create scope instance.

        Args:
            name: Scope name
            include: External scopes names for include dependencies in current scope
            __executor__: Provider executor
            **kwargs: other kwargs

        Returns: Scope instance

        """

    @abstractmethod
    def collect(self) -> None:
        """Collect scope providers."""

    @overload
    @abstractmethod
    def provide(
        self,
        provider: type[T],
        /,
        export: bool = False,
        interface: type | None = None,
    ) -> type[T]: ...
    @overload
    @abstractmethod
    def provide(
        self,
        provider: Callable[P, R],
        /,
        export: bool = False,
        interface: Callable[P, R] | None = None,
    ) -> Callable[P, R]: ...
    @abstractmethod
    def provide(
        self,
        provider: type[T] | Callable[P, R],
        /,
        export: bool = False,
        interface: type | Callable[P, R] | None = None,
    ) -> type[T] | Callable[P, R]:
        """Provide function or cls object in scope.

        Args:
            provider: Class or function object.
            export: Export providers to other scopes.
            interface: Interface for mapping.

        Returns: Passed class or function object.

        """

    @property
    @abstractmethod
    def internal_providers(self) -> MappingProxyType[str, type | Callable]:
        """Internal providers mapping."""

    @property
    @abstractmethod
    def external_providers(self) -> MappingProxyType[str, type | Callable]:
        """External providers mapping."""
