import inspect

import pytest

from dep_man.utils.inspect import add_parameters, set_signature

_test_parameters = [
    (
        inspect.Parameter(
            name="a",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=1,
            annotation=int,
        ),
    ),
    (
        inspect.Parameter(
            name="a",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=1,
            annotation=int,
        ),
        inspect.Parameter(
            name="b",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=2,
            annotation=int,
        ),
    ),
    (
        inspect.Parameter(
            name="a",
            kind=inspect.Parameter.POSITIONAL_ONLY,
            default=1,
            annotation=int,
        ),
        inspect.Parameter(
            name="b",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=2,
            annotation=int,
        ),
        inspect.Parameter(
            name="args",
            kind=inspect.Parameter.VAR_POSITIONAL,
            annotation=int,
        ),
        inspect.Parameter(
            name="c",
            kind=inspect.Parameter.KEYWORD_ONLY,
            default=4,
            annotation=int,
        ),
        inspect.Parameter(
            name="kwargs",
            kind=inspect.Parameter.VAR_KEYWORD,
            annotation=int,
        ),
    ),
]


@pytest.mark.parametrize("parameters", _test_parameters)
def test_add_parameters(parameters: tuple[inspect.Parameter, ...]):
    def foo(own: int = 1, /) -> int: ...

    old_signature = inspect.signature(foo)
    own_parameter = old_signature.parameters["own"]
    new_signature = add_parameters(old_signature, *parameters)

    assert old_signature.return_annotation == new_signature.return_annotation
    assert own_parameter == new_signature.parameters["own"]
    for parameter in parameters:
        assert parameter == new_signature.parameters[parameter.name]


@pytest.mark.parametrize("parameters", _test_parameters)
def test_set_signature(parameters: tuple[inspect.Parameter, ...]):
    def foo(own: int = 1, /) -> int: ...

    old_signature = inspect.signature(foo)
    own_parameter = old_signature.parameters["own"]
    new_signature = add_parameters(old_signature, *parameters)
    set_signature(foo, new_signature)

    assert own_parameter == new_signature.parameters["own"]
    for parameter in parameters:
        assert parameter == new_signature.parameters[parameter.name]

    defaults = [1]  # default from own attr
    kwonly_defaults = {}

    for parameter in parameters:
        if parameter.kind == inspect.Parameter.KEYWORD_ONLY:
            kwonly_defaults[parameter.name] = parameter.default
        elif parameter.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
            defaults.append(parameter.default)

    assert foo.__signature__ == new_signature  # type: ignore
    assert foo.__defaults__ == tuple(defaults)
    assert foo.__kwdefaults__ == (kwonly_defaults or None)
