"""Depend utils modules."""

import inspect
from collections.abc import Callable
from typing import Any, overload

from typing_extensions import Self


class DependValue:
    """Depend value. Return provider call result from context."""

    __executor: Callable[[str], Any]
    """Dependency manager provider executor"""

    def __init__(self, name: str, executor: Callable[[str], Any]):
        """Set name of provider."""
        self.__executor = executor
        self.name = name

    @property
    def value(self) -> Any:
        """Return provider value."""
        return self.__executor(self.name)

    def __repr__(self):
        """DependDefault representation."""
        return f"~{self.name}"


class DependParameter(inspect.Parameter):
    """Depend parameter for function signature."""

    __default: Any = inspect.Parameter.empty
    """New default value attr"""
    __executor: Callable[[str], Any]
    """Dependency manager provider executor"""

    def __init__(
        self,
        name: str,
        kind: inspect._ParameterKind,
        *,
        default: Any = inspect.Parameter.empty,
        annotation: Any = inspect.Parameter.empty,
        executor: Callable[[str], Any],
    ):
        """Set executor for depend."""
        self.__executor = executor
        super().__init__(name, kind, default=default, annotation=annotation)

    @property
    def _default(self):
        return self.__default

    @_default.setter
    def _default(self, value: str | DependValue):
        if isinstance(value, DependValue):
            value = DependValue(value.value, executor=self.__executor)
        else:
            value = DependValue(value, executor=self.__executor)

        self.__default = value


class DependDescriptor(DependValue):
    """Depend descriptor for class provider."""

    attr: str

    def __set_name__(self, owner: type, attr: str):
        """Set provider name."""
        self.attr = attr

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...
    @overload
    def __get__(self, instance: object, owner: type) -> object: ...
    def __get__(self, instance: object | None, owner: type) -> Self | object:
        """Get provider value."""
        if instance is None:
            return self

        instance.__dict__[self.attr] = self.value
        return instance.__dict__[self.attr]
