"""Base Exception class."""

from __future__ import annotations

from abc import ABCMeta
from dataclasses import Field, asdict, dataclass
from typing import Any, ClassVar, cast

from typing_extensions import dataclass_transform


@dataclass_transform(kw_only_default=True, field_specifiers=(Field,))
class ExceptionModelMeta(ABCMeta):
    """Metaclass for creating exceptions."""

    __templates__: ClassVar[set[str]] = set()
    """All templates strings"""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
    ):
        """Create dataclass from exception."""
        cls = cast("type[ExceptionModel]", super().__new__(mcs, name, bases, attrs))
        if _BaseExceptionModel in bases:
            return cls

        if not hasattr(cls, "__template__"):
            raise AttributeError(f"Attribute template is required for class {cls}")

        mcs.__templates__.add(cls.__template__)
        return dataclass(kw_only=True)(cls)

    def __call__(cls, *args, **kwargs):
        """Init exception after init dataclass."""
        instance = cast("ExceptionModel", super().__call__(*args, **kwargs))
        instance.__init_exception__()
        return instance


@dataclass(kw_only=True)
class _BaseExceptionModel(Exception):
    __template__: ClassVar[str]
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]

    def __init_exception__(self):
        """Init exception with filled template text."""
        Exception.__init__(self, self.text)

    @property
    def text(self):
        return self.__template__.format(**asdict(self))  # type: ignore


class ExceptionModel(_BaseExceptionModel, metaclass=ExceptionModelMeta):
    """Model for creating exceptions."""
