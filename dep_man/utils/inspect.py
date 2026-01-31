"""Inspect utils module."""

import inspect
import types
from collections.abc import Callable


def add_parameters(signature: inspect.Signature, *parameter: inspect.Parameter) -> inspect.Signature:
    """Add parameter to signature."""
    parameters = list(signature.parameters.values())
    parameters.extend(parameter)
    return signature.replace(parameters=parameters)


def set_signature(function: types.FunctionType | Callable, signature: inspect.Signature):
    """Add parameter to signature."""
    function.__signature__ = signature  # type: ignore
    spec = inspect.getfullargspec(function)
    function.__kwdefaults__ = spec.kwonlydefaults
    function.__defaults__ = spec.defaults
