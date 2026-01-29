"""Dep man root module."""

__all__ = [
    "dm",
    "DependencyManager",
    "BaseDependencyManager",
    "Scope",
    "Injector",
]

from dep_man.core.injectors import Injector
from dep_man.core.managers import BaseDependencyManager, DependencyManager, dm
from dep_man.core.scopes import Scope
