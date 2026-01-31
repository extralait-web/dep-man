"""DI manager interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Generic, overload

from typing_extensions import Self, TypedDict

from dep_man.consts import DEFAULT_DEPENDENCIES_FILE_NAME
from dep_man.core.injectors import TInjector
from dep_man.core.scopes import TScope

if TYPE_CHECKING:
    from collections.abc import Callable

    from dep_man.types import P, ProvidersType, R, ScopeNameType, T
    from dep_man.utils.contextvar import SimpleContext


class InitCache(TypedDict):
    """Cache of init method call."""

    providers: ProvidersType
    globalize: bool | tuple[ScopeNameType]


class IDependencyManager(ABC, Generic[TScope, TInjector]):
    """DI manager interface."""

    __loaded__: ClassVar[bool]
    """Is manager loaded"""
    __inited__: ClassVar[bool]
    """Is manager inited"""
    __forks_count__: ClassVar[int]
    """Dependency manager forks."""
    __context__: ClassVar[SimpleContext[ProvidersType]]
    """Dependency manager context."""
    # noinspection PyClassVar
    __injector_type__: ClassVar[type[TInjector]]  # pyright: ignore[reportGeneralTypeIssues]
    """Injector type used in inject call"""
    # noinspection PyClassVar
    __scope_type__: ClassVar[type[TScope]]  # pyright: ignore[reportGeneralTypeIssues]
    """Scopes type used in add_scope method"""
    # noinspection PyClassVar
    __scopes__: ClassVar[dict[ScopeNameType, TScope]]  # pyright: ignore[reportGeneralTypeIssues]
    """Scopes container with dependencies"""

    @classmethod
    @abstractmethod
    def load(
        cls,
        *packages: str,
        file_name: str = DEFAULT_DEPENDENCIES_FILE_NAME,
        reload: bool = False,
    ):
        """Load dependencies.

        Args:
            *packages: Tuple of package names like [ext_dev.directory]
            file_name: File name with providing dependencies by default it's "dependencies"
            reload: Reload dependencies.

        """

    @classmethod
    @abstractmethod
    def init(cls, globalize: bool | tuple[ScopeNameType] = False, reinit: bool = False):
        """Init dependency manager context.

        Args:
            globalize: Add all or certain scopes providers in global context for using providers without context managers
            reinit: Reinit manager context

        """

    @classmethod
    @abstractmethod
    def fork(cls, name: str | None = None) -> type[Self]:
        """Make new class object with own context and scopes."""

    @classmethod
    @abstractmethod
    def add_scope(cls, name: ScopeNameType, include: tuple[ScopeNameType, ...] = (), **kwargs) -> TScope:
        """Add a scope to the manager.

        Args:
            name: Scope name
            include: Include dependencies from other scopes
            **kwargs: Other kwargs

        """

    @classmethod
    @abstractmethod
    def resolve(cls, *scopes: ScopeNameType) -> ProvidersType:
        """Resolve scopes providers.

        Args:
            *scopes: Scopes names for providers aggregation

        Returns: total providers dict

        """

    @overload
    @classmethod
    @abstractmethod
    def provide(
        cls,
        provider: type[T],
        /,
        scope: ScopeNameType | None = None,
        export: bool = False,
        interface: type | None = None,
    ) -> type[T]: ...
    @overload
    @classmethod
    @abstractmethod
    def provide(
        cls,
        provider: Callable[P, R],
        /,
        scope: ScopeNameType | None = None,
        export: bool = False,
        interface: Callable[P, R] | None = None,
    ) -> Callable[P, R]: ...
    @classmethod
    @abstractmethod
    def provide(
        cls,
        provider: type[T] | Callable[P, R],
        /,
        scope: ScopeNameType | None = None,
        export: bool = False,
        interface: type | Callable[P, R] | None = None,
    ) -> type[T] | Callable[P, R]:
        """Provide function or cls object.

        Args:
            provider: Class or function object.
            scope: dependency storage scope
            export: Export providers to other scopes.
            interface: Interface for mapping.

        Returns: Passed class or function object.

        """

    @overload
    @classmethod
    @abstractmethod
    def inject(cls, scope_or_target: type[T], *scopes: ScopeNameType) -> type[T]: ...
    @overload
    @classmethod
    @abstractmethod
    def inject(cls, scope_or_target: Callable[P, R], *scopes: ScopeNameType) -> Callable[P, R]: ...
    @overload
    @classmethod
    @abstractmethod
    def inject(cls, scope_or_target: ScopeNameType, *scopes: ScopeNameType) -> TInjector: ...
    @classmethod
    @abstractmethod
    def inject(
        cls, scope_or_target: type[T] | Callable[P, R] | ScopeNameType, *scopes: ScopeNameType
    ) -> type[T] | Callable[P, R] | TInjector:
        """Return inject providers.

        Args:
            scope_or_target: Class or function object if decorate without call or scope name for parametrized call.
            *scopes: scopes names

        Returns: Class or function object if decorate without call or Injector for decoration

        """

    @classmethod
    @abstractmethod
    def execute_provider(cls, name: str, scope: ScopeNameType | None = None) -> Any:
        """Execute provider with given name and return result.

        Args:
            name: provider name
            scope: provider scope name

        Returns: provider call result.

        """
