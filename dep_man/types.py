"""Module types."""

import sys
from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any, TypeAlias

from typing_extensions import ParamSpec, Protocol, TypeVar

T = TypeVar("T")
F = TypeVar("F")
P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class __DependType__:
    """Special type for dependency detection."""


class __FDependType__:
    """Special type for function dependency detection."""


Depend = Annotated[T, __DependType__]
"""Depend type for provide classes"""

if TYPE_CHECKING:
    FDepend = Annotated
    """FDepend type for provide functions results"""
else:

    class FDepend:
        """Real "FDepend" annotation which bind __DependType__ when call Annotated.__class_getitem__."""

        def __class_getitem__(cls, params):
            """Proxy call in Annotated.__class_getitem__ with special type in metadata."""
            params = (*params, __FDependType__)
            if sys.version_info < (3, 13):
                return Annotated.__class_getitem__(params)  # type: ignore
            return Annotated.__getitem__(params)


class BIND:  # pyright: ignore [reportRedeclaration]
    """Class for using in function defaults."""


# We specify as Any for using BIND as function arg default value to avoid breaking type checking
BIND: Any

ScopeNameType: TypeAlias = str | Enum
"""Scope name type"""

ProvidersType: TypeAlias = dict[str, type | Callable]
"""Provider container type alias"""


class PExecutor(Protocol):
    """Provider executor type alias."""

    def __call__(self, name: str, scope: ScopeNameType | None = None) -> Any:
        """Method call."""
