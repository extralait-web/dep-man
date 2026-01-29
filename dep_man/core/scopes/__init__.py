"""Scopes module."""

__all__ = [
    "TScope",
    "IScope",
    "Scope",
]

from typing_extensions import TypeVar

from dep_man.core.scopes.bases import Scope
from dep_man.core.scopes.interfaces import IScope

TScope = TypeVar("TScope", bound=IScope, default=Scope)
