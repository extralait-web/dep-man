"""Module exceptions."""

from dep_man.utils.exceptions import ExceptionModel


class _WrongDependencyManagerGenericArg(ValueError, ExceptionModel):
    __arg_name__: str = ""

    name: str
    value: str

    __template__ = (
        "{name} passed wrong generic arg of class BaseDependencyManager. "
        "T{__arg_name__} expected I{__arg_name__} subclass, but {value} was given."
    )


class WrongScopeTypeException(_WrongDependencyManagerGenericArg):
    """Raised when passed wrong generic attr in BaseDependencyManager."""

    __arg_name__: str = "Scope"


class WrongInjectorTypeException(_WrongDependencyManagerGenericArg):
    """Raised when passed wrong generic attr in BaseDependencyManager."""

    __arg_name__: str = "Injector"


class _ScopeItemException(KeyError, ExceptionModel):
    __attr_name__: str = ""

    name: str
    scope: str

    __template__ = "{__attr_name__} {name} already exists in scope {scope}"


class DependencyAlreadyExistsException(_ScopeItemException):
    """Raised when dependency is already present in certain scope."""

    __attr_name__: str = "Dependency"


class InterfaceAlreadyExistsException(_ScopeItemException):
    """Raised when interface is already present in certain scope."""

    __attr_name__: str = "Interface"


class InterfaceNameOverlapWithProviderException(KeyError, ExceptionModel):
    """Raised when interface name present in certain scope dependencies."""

    name: str
    scope: str

    __template__ = "Interface {name} name overlap with scope {scope} dependencies"


class ScopeDoesNotExistsException(KeyError, ExceptionModel):
    """Raised when a scope was not added to DependencyManager."""

    name: str
    manager: str

    __template__ = (
        "Scope {name} does not exist in {manager}.__scopes__. Use {manager}.add_scope for add scope in __scopes__"
    )


class ScopeAlreadyExistsException(KeyError, ExceptionModel):
    """Raised when a scope already added to DependencyManager."""

    name: str
    manager: str

    __template__ = "Scope {name} already exists in {manager}.__scopes__."


class ScopeTypeNotSetException(ValueError, ExceptionModel):
    """Raised when a __scope_type__ not set in DependencyManager."""

    manager: str

    __template__ = "Scope type not passed in Generic arg for BaseDependencyManager in {manager} class declaration"


class ProviderDoesNotExistsInContextException(KeyError, ExceptionModel):
    """Raised when a provider not present in context or scope."""

    name: str
    scope: str

    __template__ = "Provider {name} does not exist in context and scope {scope}."


class ClassBaseInjectionContextDoesNotSupport(ValueError, ExceptionModel):
    """Raised when a dm.inject call on class with scope passing."""

    name: str

    __template__ = (
        "Scopes base injection with class target does not support. "
        "Remove scopes passing in dm.inject call on class {name}."
    )


class ProviderAlreadyProvidedException(ValueError, ExceptionModel):
    """Raised when a provider already provided."""

    name: str

    __template__ = "Provider {name} already provided."


class DependencyManagerAlreadyLoaded(RuntimeError, ExceptionModel):
    """Raised when a call load method of DependencyManager on loaded manager without reload flag."""

    name: str

    __template__ = (
        "Dependency manager {name} already loaded. If you really need reload all dependencies use reload=True."
    )


class DependencyManagerAlreadyInited(RuntimeError, ExceptionModel):
    """Raised when a call init method of DependencyManager on inited manager without reinit flag and different globalize."""

    name: str

    __template__ = (
        "Dependency manager {name} already inited but globalize value was changed. "
        "If you really need reinit manager context use reinit=True."
    )
