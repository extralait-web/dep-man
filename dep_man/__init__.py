"""Dep man root module."""

__all__ = [
    "__version__",
    "dm",
    "get_django_middleware",
    "get_starlette_middleware",
    "DependencyManager",
    "BaseDependencyManager",
    "Scope",
    "Injector",
]

from dep_man.core.injectors import Injector
from dep_man.core.managers import BaseDependencyManager, DependencyManager, dm
from dep_man.core.scopes import Scope
from dep_man.integrations.django import get_django_middleware
from dep_man.integrations.starlette import get_starlette_middleware

from .version import VERSION

__version__ = VERSION
