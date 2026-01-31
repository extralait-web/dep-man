import inspect
from typing import Any

import pytest

from dep_man.core.depend import DependDescriptor, DependParameter, DependValue
from dep_man.types import ScopeNameType

parameters = {
    "name1": 1,
    "name2": 2,
}


def executor(name: str, scope: ScopeNameType | None = None):
    return parameters[name]


parametrizer = pytest.mark.parametrize("name,value", parameters.items())


@parametrizer
def test_depend_value(name: str, value: Any):
    depend = DependValue(name, executor)
    assert str(depend) == f"~{name}"
    assert depend.value == value


@parametrizer
def test_depend_parameter(name: str, value: Any):
    parameter = DependParameter(
        name=name,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        default=name,
        executor=executor,
    )
    assert parameter.default.value == value


@parametrizer
def test_depend_descriptor(name: str, value: Any):
    class Foo: ...

    descriptor = DependDescriptor(name=name, executor=executor)

    setattr(Foo, name, descriptor)
    getattr(Foo, name).__set_name__(Foo, name)

    assert getattr(Foo, name) == descriptor
    assert getattr(Foo(), name) == value
