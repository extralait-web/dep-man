"""Utils for working with builtins."""

import types
from collections.abc import Callable
from copy import copy


def copy_func(function: types.FunctionType | Callable, name=None):
    """Copy function.

    Args:
        function: function to be copied
        name: new function name

    Returns: function copy

    """
    function_copy = types.FunctionType(
        code=function.__code__,
        globals=function.__globals__,
        name=name or function.__name__,
        argdefs=function.__defaults__,
        closure=function.__closure__,
    )
    # in case f was given attrs (note this dict is a shallow copy):
    function_copy.__dict__ = function.__dict__
    # copy __kwdefaults__
    function_copy.__kwdefaults__ = copy(getattr(function, "__kwdefaults__", None))  # type: ignore
    return function_copy
