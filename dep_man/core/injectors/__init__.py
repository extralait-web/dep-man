"""Injectors module."""

__all__ = [
    "TInjector",
    "IInjector",
    "Injector",
]

from typing_extensions import TypeVar

from dep_man.core.injectors.bases import Injector
from dep_man.core.injectors.interfaces import IInjector

TInjector = TypeVar("TInjector", bound=IInjector, default=Injector)
