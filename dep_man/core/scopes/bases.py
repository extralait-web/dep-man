"""Bases scope class."""

from __future__ import annotations

from functools import partial
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, overload

from dep_man.core.exceptions import (
    DependencyAlreadyExistsException,
    InterfaceAlreadyExistsException,
    InterfaceNameOverlapWithProviderException,
)
from dep_man.core.mocker import mock_provider
from dep_man.core.schemas import Dependency
from dep_man.core.scopes.interfaces import IScope

if TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import Self

    from dep_man.types import P, PExecutor, ProvidersType, R, ScopeNameType, T


class Scope(IScope):
    """Class for scope management."""

    _internal_providers: ProvidersType
    _external_providers: ProvidersType
    _dependencies: dict[str, Dependency]
    _interfaces: dict[str, Dependency]
    _kwargs: dict[str, Any]

    def __init__(
        self,
        name: ScopeNameType,
        include: tuple[ScopeNameType, ...] = (),
        *,
        __executor__: PExecutor,
        **_kwargs: Any,
    ):
        """Create scope instance.

        Args:
            name: Scope name
            include: External scopes names for include _dependencies in current scope
            __executor__: Provider executor
            **_kwargs: other _kwargs

        Returns: Scope instance

        """
        self.name = name
        self.include = include

        self._internal_providers = {}
        self._external_providers = {}
        self._dependencies = {}
        self._interfaces = {}
        self._kwargs = _kwargs

        self.__executor__ = __executor__
        self.__resolve_cache__ = None

    @classmethod
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
            include: External scopes names for include _dependencies in current scope
            __executor__: Provider executor
            **_kwargs: other _kwargs

        Returns: Scope instance

        """
        return cls(name=name, include=include, __executor__=__executor__, **_kwargs)

    def collect(self) -> None:  # pyright: ignore [reportIncompatibleMethodOverride]
        """Collect scope providers."""
        # for reload case clear containers
        self._internal_providers = {}
        self._external_providers = {}
        self.__resolve_cache__ = None

        # iter by _dependencies dict
        for name, dependency in self._dependencies.items():
            # add provider to internal providers
            self._internal_providers[name] = dependency.provider
            # add provider to external providers if export is True
            if dependency.export:
                self._external_providers[name] = dependency.provider

        # iter by _interfaces dict
        for name, dependency in self._interfaces.items():
            # add provider to internal providers by interface name
            self._internal_providers[name] = dependency.provider
            # add provider to external providers by interface name if export is True
            if dependency.export:
                self._external_providers[name] = dependency.provider

    @overload
    def provide(
        self,
        provider: type[T],
        /,
        export: bool = False,
        interface: type | None = None,
    ) -> type[T]: ...
    @overload
    def provide(
        self,
        provider: Callable[P, R],
        /,
        export: bool = False,
        interface: Callable[P, R] | None = None,
    ) -> Callable[P, R]: ...
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
        # dependency must hame unique name
        if provider.__name__ in self._dependencies:
            # otherwise raise exception
            raise DependencyAlreadyExistsException(name=provider.__name__, scope=str(self.name))

        mock_provider(provider, partial(self.__executor__, scope=self.name))

        dependency = self._dependencies[provider.__name__] = Dependency(
            name=provider.__name__,
            provider=provider,
            export=export,
            interface=interface,
        )

        # if interface was passed try to add new interface
        if interface:
            # interface name must be unique in scope
            if interface.__name__ in self._interfaces:
                # otherwise raise exception
                raise InterfaceAlreadyExistsException(name=interface.__name__, scope=str(self.name))

            # dependency and interface names must not overlap
            if interface.__name__ in self._dependencies:
                # otherwise raise exception
                raise InterfaceNameOverlapWithProviderException(name=interface.__name__, scope=str(self.name))

            # add interface in manager scope
            self._interfaces[interface.__name__] = dependency

        return provider

    @property
    def internal_providers(self) -> MappingProxyType[str, type | Callable]:
        """Internal providers mapping."""
        return MappingProxyType(self._internal_providers)

    @property
    def external_providers(self) -> MappingProxyType[str, type | Callable]:
        """External providers mapping."""
        return MappingProxyType(self._external_providers)
