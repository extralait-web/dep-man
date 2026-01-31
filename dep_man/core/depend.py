"""Depend utils modules."""

import inspect
from typing import Any, overload

from typing_extensions import Self

from dep_man.types import PExecutor


class DependValue:
    """Depend value. Return provider call result from context."""

    __executor: PExecutor
    """Dependency manager provider executor"""

    def __init__(self, name: str, executor: PExecutor):
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
    __executor: PExecutor
    """Dependency manager provider executor"""

    def __init__(
        self,
        name: str,
        kind: inspect._ParameterKind,
        *,
        default: Any = inspect.Parameter.empty,
        annotation: Any = inspect.Parameter.empty,
        executor: PExecutor,
    ):
        """Set executor for depend."""
        self.__executor = executor
        super().__init__(name, kind, default=default, annotation=annotation)

    @property
    def _default(self) -> DependValue:
        return self.__default

    @_default.setter
    def _default(self, value: str):
        self.__default = DependValue(value, executor=self.__executor)


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
