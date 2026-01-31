"""Bases DI managers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, cast, get_args, get_origin, overload

from typing_extensions import Self

from dep_man.consts import DEFAULT_DEPENDENCIES_FILE_NAME
from dep_man.core.exceptions import (
    ClassBaseInjectionContextDoesNotSupport,
    DependencyManagerAlreadyInited,
    DependencyManagerAlreadyLoaded,
    ProviderDoesNotExistsInContextException,
    ScopeAlreadyExistsException,
    ScopeDoesNotExistsException,
    WrongInjectorTypeException,
    WrongScopeTypeException,
)
from dep_man.core.injectors import TInjector
from dep_man.core.injectors.interfaces import IInjector
from dep_man.core.managers.interfaces import IDependencyManager, InitCache
from dep_man.core.scopes import TScope
from dep_man.core.scopes.interfaces import IScope
from dep_man.types import P, ProvidersType, R, ScopeNameType, T
from dep_man.utils.contextvar import SimpleContext


class BaseDependencyManager(IDependencyManager[TScope, TInjector], Generic[TScope, TInjector]):
    """Base DI manager."""

    def __init_subclass__(cls):
        """Set new __scopes__ object and __scope_type__."""
        super().__init_subclass__()

        # set state
        cls.__loaded__ = False
        cls.__inited__ = False
        cls.__init_cache__ = InitCache(providers={}, globalize=False)
        # set new forks
        cls.__forks_count__ = 0
        # set new scopes
        cls.__scopes__ = {}
        # set manager context
        cls.__context__ = SimpleContext[ProvidersType](default_factory=dict)

        # if __scope_type__ already set just return
        if hasattr(cls, "__scope_type__") and hasattr(cls, "__injector_type__"):
            return

        # iter by __orig_bases__
        for base in cls.__orig_bases__:  # type:ignore
            # if base class is _GenericAlias getting original object (search BaseDependencyManager)
            if get_origin(base) is not BaseDependencyManager and base is not BaseDependencyManager:
                continue

            args = get_args(base)
            cls.__save_generic_args__(args)
            # exit from function
            return

        # if generic args was not passed check __base__ class
        cls.__save_generic_args__(())  # type: ignore

    @classmethod
    def __save_generic_args__(cls, args: tuple[type, ...]):
        """Save generic args in cls attrs from passed args."""
        scope_type = args[0] if len(args) else TScope.__default__
        if not issubclass(scope_type, IScope):
            raise WrongScopeTypeException(name=cls.__name__, value=scope_type.__name__)

        cls.__scope_type__ = scope_type  # pyright: ignore [reportAttributeAccessIssue]

        injector_type = args[1] if len(args) > 1 else TInjector.__default__  # type: ignore
        if not issubclass(injector_type, IInjector):
            raise WrongInjectorTypeException(name=cls.__name__, value=injector_type.__name__)

        cls.__injector_type__ = injector_type  # pyright: ignore [reportAttributeAccessIssue]

    @classmethod
    def _import_module(cls, module_name: str):
        """Import module for initialize module providers."""
        __import__(module_name)

    @classmethod
    def load(
        cls,
        *packages: str,
        file_name: str | None = DEFAULT_DEPENDENCIES_FILE_NAME,
        reload: bool = False,
    ):
        """Load dependencies.

        Args:
            *packages: Tuple of package names like [ext_dev.directory]
            file_name: File name with providing dependencies by default it's "dependencies"
            reload: Reload dependencies.

        """
        if cls.__loaded__ and not reload:
            raise DependencyManagerAlreadyLoaded(name=cls.__name__)

        # import modules for initialize not initialized modules
        for package in packages:
            cls._import_module(f"{package}.{file_name}" if file_name else package)

        # collect total scope providers
        for scope in cls.__scopes__.values():
            scope.collect()

        cls.__loaded__ = True

    @classmethod
    def init(cls, globalize: bool | tuple[ScopeNameType] = False, reinit: bool = False):
        """Init dependency manager context.

        Args:
            globalize: Add all or certain scopes providers in global context for using providers without context managers
            reinit: Reinit manager context

        """
        # if manager already inited, set value from cache
        if cls.__inited__ and not reinit:
            # if global scopes was changed, raise exception
            if globalize != cls.__init_cache__["globalize"]:
                raise DependencyManagerAlreadyInited(name=cls.__name__)

            # set providers context from cache
            cls.__context__.__init_context__({**cls.__init_cache__["providers"]})
            return

        scopes = None
        # if globalize is True use all scopes as global
        if globalize is True:
            scopes = tuple(cls.__scopes__.keys())
        # if passed certain scopes use it
        elif globalize:
            scopes = globalize

        providers = {}
        # if we have global scopes get scopes providers
        if scopes:
            providers = cls.resolve(*scopes)

        # initial context with provider dict
        cls.__context__.__init_context__(providers)

        # set init state
        cls.__inited__ = True
        cls.__init_cache__ = InitCache(providers={**providers}, globalize=globalize)

    @classmethod
    def fork(cls, name: str | None = None) -> type[Self]:
        """Make new class object with own context and scopes.

        Args:
            name: Name of new class, by default use "{cls.__name__}_{cls.__forks_count__}"

        Returns: New DependencyManager class

        """
        cls.__forks_count__ += 1
        name = name or f"{cls.__name__}_{cls.__forks_count__}"
        return type(cls)(name, (cls,), {"__module__": cls.__module__})

    @classmethod
    def add_scope(cls, name: ScopeNameType, include: tuple[ScopeNameType, ...] = (), **kwargs) -> TScope:
        """Add a scope to the manager.

        Args:
            name: Scope name
            include: Include dependencies from other scopes
            **kwargs: other kwargs

        """
        # scope name must bge unique
        if name in cls.__scopes__:
            raise ScopeAlreadyExistsException(name=str(name), manager=cls.__name__)

        # add new scope in manager
        cls.__scopes__[name] = cls.__scope_type__.create(
            name=name,
            include=include,
            **kwargs,
            __executor__=cls.execute_provider,
        )
        return cls.__scopes__[name]

    @classmethod
    def resolve(cls, *scopes: ScopeNameType) -> ProvidersType:
        """Resolve scopes providers.

        Args:
            *scopes: Scopes names for providers aggregation

        Returns: total providers dict

        """
        providers: ProvidersType = {}
        # iter by passed scopes
        for scope in scopes:
            # get current scope from cls scopes
            scope_object = cls.__scopes__[scope]

            # check resolve cache
            if scope_object.__resolve_cache__ is not None:
                providers.update(scope_object.__resolve_cache__)
                continue

            # container for scope providers
            scope_resolve = {}
            # add included scopes providers which marked as export
            for included in scope_object.include:
                external_providers = cls.__scopes__[included].external_providers
                scope_resolve.update(external_providers)

            # update scope providers from internal scope providers
            scope_resolve.update(scope_object.internal_providers)

            # set scope resolve cache
            scope_object.__resolve_cache__ = scope_resolve
            providers.update(scope_resolve)

        return providers

    @overload
    @classmethod
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
    def provide(
        cls,
        provider: Callable[P, R],
        /,
        scope: ScopeNameType | None = None,
        export: bool = False,
        interface: Callable[P, R] | None = None,
    ) -> Callable[P, R]: ...
    @classmethod
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
        # scope must be presented in the manager
        if scope not in cls.__scopes__:
            # otherwise raise exception
            raise ScopeDoesNotExistsException(name=str(scope), manager=cls.__name__)

        # getting certain scope provide method
        scope_provide = cls.__scopes__[scope].provide
        # pyright have some problems with nested overload
        scope_provide(provider, export=export, interface=interface)  # pyright: ignore [reportArgumentType, reportCallIssue]

        return provider

    @overload
    @classmethod
    def inject(cls, scope_or_target: type[T], *scopes: ScopeNameType) -> type[T]: ...
    @overload
    @classmethod
    def inject(cls, scope_or_target: Callable[P, R], *scopes: ScopeNameType) -> Callable[P, R]: ...
    @overload
    @classmethod
    def inject(cls, scope_or_target: ScopeNameType, *scopes: ScopeNameType) -> TInjector: ...
    @classmethod
    def inject(
        cls, scope_or_target: type[T] | Callable[P, R] | ScopeNameType, *scopes: ScopeNameType
    ) -> type[T] | Callable[P, R] | TInjector:
        """Return inject providers.

        Args:
            scope_or_target: Class or function object if decorate without call or scope name for parametrized call.
            *scopes: scopes names

        Returns: Class or function object if decorate without call or Injector for decoration

        """
        kwargs = {"__executor__": cls.execute_provider, "__context__": cls.__context__}

        # if first arg is class return class
        if isinstance(scope_or_target, type):
            if scopes:
                # if scopes was passed raise error
                raise ClassBaseInjectionContextDoesNotSupport(name=scope_or_target.__name__)

            # create injector and call it instance for return class object
            return cls.__injector_type__.create(None, **kwargs)(scope_or_target)

        # if first arg is function return function
        if isinstance(scope_or_target, Callable):
            # if scopes was not passed use all scopes
            if not scopes:
                scopes = tuple(cls.__scopes__.keys())

            # get scopes providers
            providers = cls.resolve(*scopes)
            # create injector and call it instance for return function object
            return cls.__injector_type__.create(providers, **kwargs)(scope_or_target)

        scope_or_target = cast("ScopeNameType", scope_or_target)
        # get scopes providers
        providers = cls.resolve(scope_or_target, *scopes)
        # return injector instance for decorating or use as context manager
        return cls.__injector_type__.create(providers, **kwargs)

    @classmethod
    def execute_provider(cls, name: str, scope: ScopeNameType | None = None):
        """Execute provider with given name and return result.

        Args:
            name: provider name
            scope: provider scope name

        Returns: provider call result.

        """
        provider = cls.__context__.value.get(name)

        if provider is None and scope:
            provider = cls.resolve(scope).get(name)

        if provider is None:
            raise ProviderDoesNotExistsInContextException(name=name, scope=str(scope) if scope else "")
        return provider()


class DependencyManager(BaseDependencyManager):
    """Default dependency manager."""


dm = DependencyManager
