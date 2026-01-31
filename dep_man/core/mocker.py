"""Provider module."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from dep_man.core.depend import DependDescriptor, DependParameter, DependValue
from dep_man.core.exceptions import ProviderAlreadyProvidedException
from dep_man.utils.annotations import get_signature_parameters_providers, parse_provider_name_from_annotation
from dep_man.utils.builtins import copy_func
from dep_man.utils.inspect import (
    add_parameters,
    set_signature,
)

if TYPE_CHECKING:
    import types

    from dep_man.types import PExecutor


def __get_proxy_provider_function_arguments(
    *args,
    __proxy_provider_function_original: Callable,
    __proxy_provider_function_signature: inspect.Signature,
    **kwargs,
) -> tuple[list, dict]:
    """Get proxy provider function arguments.

    Args:
        *args: Any args for __proxy_provider_function_original
        __proxy_provider_function_original: bind from inserted signature parameter.default value
        __proxy_provider_function_signature: bind from inserted signature parameter.default value
        **kwargs: Any kwargs for __proxy_provider_function_original

    Returns: args and kwargs for __proxy_provider_function_original call

    """
    # bind passed args and kwargs
    bound = __proxy_provider_function_signature.bind(*args, **kwargs)
    # apply defaults values of signature
    bound.apply_defaults()

    # make new args with DependDefault values
    new_args = []
    for arg in bound.args:
        if isinstance(arg, DependValue):
            new_args.append(arg.value)
        else:
            new_args.append(arg)

    # make new kwargs with DependDefault values
    new_kwargs = {}
    for key, value in bound.kwargs.items():
        if isinstance(value, DependValue):
            new_kwargs[key] = value.value
        else:
            new_kwargs[key] = value

    return new_args, new_kwargs


def __proxy_provider_function(
    *args,
    __proxy_provider_function_original: Callable,
    __proxy_provider_function_signature: inspect.Signature,
    **kwargs,
) -> Any:
    """Sync proxy provider function.

    Args:
        *args: Any args for __proxy_provider_function_original
        __proxy_provider_function_original: bind from inserted signature parameter.default value
        __proxy_provider_function_signature: bind from inserted signature parameter.default value
        **kwargs: Any kwargs for __proxy_provider_function_original

    Returns: original function return type

    """
    _args, _kwargs = __get_proxy_provider_function_arguments(
        *args,
        __proxy_provider_function_original=__proxy_provider_function_original,
        __proxy_provider_function_signature=__proxy_provider_function_signature,
        **kwargs,
    )
    return __proxy_provider_function_original(*_args, **_kwargs)


async def __async_proxy_provider_function(
    *args,
    __proxy_provider_function_original: Callable[..., Awaitable],
    __proxy_provider_function_signature: inspect.Signature,
    **kwargs,
) -> Any:
    """Async proxy provider function.

    Args:
        *args: Any args for __proxy_provider_function_original
        __proxy_provider_function_original: bind from inserted signature parameter.default value
        __proxy_provider_function_signature: bind from inserted signature parameter.default value
        **kwargs: Any kwargs for __proxy_provider_function_original

    Returns: original function return type

    """
    _args, _kwargs = __get_proxy_provider_function_arguments(
        *args,
        __proxy_provider_function_original=__proxy_provider_function_original,
        __proxy_provider_function_signature=__proxy_provider_function_signature,
        **kwargs,
    )
    return await __proxy_provider_function_original(*_args, **_kwargs)


def __make_proxy_provider_signature(function: types.FunctionType, signature: inspect.Signature):
    """Make proxy provider signature. Add __proxy_provider_function required parameters to signature.

    Args:
        function: function for calling in __proxy_provider_function
        signature: signature for __proxy_provider_function

    Returns: New signature with proxy parameters

    """
    return add_parameters(
        signature,
        # original function parameter
        inspect.Parameter(
            name="__proxy_provider_function_original",
            kind=inspect.Parameter.KEYWORD_ONLY,
            # make kopy of function for avoid unexpected behavior
            default=copy_func(function),  # type: ignore
            annotation=Callable,
        ),
        # signature parameter
        inspect.Parameter(
            name="__proxy_provider_function_signature",
            kind=inspect.Parameter.KEYWORD_ONLY,
            default=signature,
            annotation=Callable,
        ),
    )


def __make_proxy_provider_function(
    function: types.FunctionType,
    signature: inspect.Signature,
    sync: bool = True,
):
    """Make proxy provider function. Make copy of __proxy_provider_function and change signature.

    Args:
        function: function for calling in __proxy_provider_function
        signature: signature for __proxy_provider_function
        sync: use sync or async version of __proxy_provider_function

    Returns: Copy of __proxy_provider_function

    """
    # add proxy params to signature
    __proxy_provider_signature = __make_proxy_provider_signature(function, signature)
    # copy __proxy_provider_function
    if sync:
        # get sync function copy
        __proxy_provider_function_copy = copy_func(__proxy_provider_function)
    else:
        # get async function copy
        __proxy_provider_function_copy = copy_func(__async_proxy_provider_function)
    # change function signature
    set_signature(__proxy_provider_function_copy, __proxy_provider_signature)
    # return copy with changed signature
    return __proxy_provider_function_copy


def __replace_providers_parameters(signature: inspect.Signature, executor: PExecutor) -> inspect.Signature:
    """Merge parameters with provider names.

    Args:
        signature: original function signature
        executor: provider executor

    Returns: new signature for original function

    """
    # get params providers mapping
    providers = get_signature_parameters_providers(signature)

    parameters = []
    # iter by signature params
    for name, parameter in signature.parameters.items():
        provider_name = providers.get(name)

        # if not provider name add common signature parameter
        if not provider_name:
            parameters.append(parameter)
            continue

        # otherwise add "depend" parameter with provider name as default value and executor
        parameters.append(
            DependParameter(
                parameter.name,
                kind=parameter.kind,
                default=provider_name,
                annotation=parameter.annotation,
                executor=executor,
            )
        )

    # create signature with new parameters
    return signature.replace(parameters=parameters)


def _mock_callable_provider(function: Callable | types.FunctionType, executor: PExecutor):
    """Make provider function from callable object.

    Args:
        function: function for mocking
        executor: provider executor

    """
    # get original function
    unwrapped = inspect.unwrap(function)
    # check if the function has been mock
    if getattr(unwrapped, "__mocked_provider__", None):
        raise ProviderAlreadyProvidedException(name=unwrapped.__name__)

    # get original function signature
    signature = inspect.signature(unwrapped)
    # change default values for parameters with "Depend" and "FDepend" annotations
    signature = __replace_providers_parameters(signature, executor)
    # make proxy provider function
    if inspect.iscoroutinefunction(unwrapped):
        # make async function
        proxy_provider_function = __make_proxy_provider_function(unwrapped, signature, False)
    else:
        # make sync function
        proxy_provider_function = __make_proxy_provider_function(unwrapped, signature, True)
    # change code of original function
    unwrapped.__code__ = proxy_provider_function.__code__
    # add in unwrapped globals variables from outer namespace for __(async)?proxy_provider_function
    unwrapped.__globals__["__get_proxy_provider_function_arguments"] = __get_proxy_provider_function_arguments
    # change signature of original function
    set_signature(unwrapped, inspect.signature(proxy_provider_function))
    # mark original function as provided
    unwrapped.__mocked_provider__ = True


def _mock_class_provider(cls: type, executor: PExecutor):
    """Make provider cls from class object.

    Args:
        cls: class object for mocking
        executor: provider executor

    """
    # check if the class has been mock
    if cls.__dict__.get("__mocked_provider__", None):
        raise ProviderAlreadyProvidedException(name=cls.__name__)

    providers = {}
    # iter by mro for collect all bases annotations
    for _cls in reversed(cls.__mro__):
        _annotations = inspect.get_annotations(_cls)
        # iter by annotations
        for attr, annotation in _annotations.items():
            # try parse provider name from annotation
            provider_name = parse_provider_name_from_annotation(annotation)
            # if not provider name go to next annotation
            if not provider_name:
                continue

            # otherwise add provider in dict
            providers[attr] = provider_name

    # iter by providers attrs
    for attr, provider_name in providers.items():
        # if cls already have attr we need check provider name
        if attr_value := getattr(cls, attr, None):
            # if providers names is same go tu next provider
            if isinstance(attr_value, DependDescriptor) and attr_value.name == provider_name:
                continue

        # otherwise set new DependDescriptor to class
        setattr(cls, attr, DependDescriptor(provider_name, executor=executor))
        # call __set_name__ on descriptor because the descriptor is not set when the class is declared
        getattr(cls, attr).__set_name__(cls, attr)

    # mark class as provided
    cls.__mocked_provider__ = True


def mock_provider(provider: type | Callable, executor: PExecutor) -> None:
    """Mock class or function provider.

    Args:
        provider: class or function for mocking
        executor: provider executor

    """
    if isinstance(provider, type):
        _mock_class_provider(provider, executor)
    else:
        _mock_callable_provider(provider, executor)
