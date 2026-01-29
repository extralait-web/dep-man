"""Module schemas."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(kw_only=True)
class Dependency:
    """Dependency dataclass."""

    name: str
    provider: type | Callable
    export: bool = False
    interface: type | Callable | None = None
