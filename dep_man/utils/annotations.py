"""Module util for working with annotations."""

import inspect
import re
from collections.abc import Sequence
from typing import Annotated, Any, ForwardRef, Optional, Protocol, TypeVar, Union, get_args, get_origin

from dep_man.types import __DependType__, __FDependType__

_depend_pattern = re.compile(r"(.* |^)(Optional\[)?Depend\[(.*?)].*")
"""Pattern for Depend annotation like Depend[ProviderClass]"""
_function_depend_pattern = re.compile(r"(.* |^)(Optional\[)?FDepend\[.+, (.*?)].*")
"""Pattern for FDepend annotation like FDepend[bool, provider_function]"""


def is_optional(annotation):
    """Check if annotation is optional or not."""
    if annotation is Optional:
        return True
    return get_origin(annotation) is Union and type(None) in get_args(annotation)


def is_annotated(annotation):
    """Check if annotation is optional or not."""
    return get_origin(annotation) is Annotated


class _PAnnotated(Protocol):
    """Runtime checkable protocol for Annotated detection."""

    __args__: Sequence
    __metadata__: Sequence


def _parse_provider_name_from_string_annotation(annotation: str):
    """Return provider name from str annotation.

    Args:
        annotation: string annotation from param annotation.

    Returns: provider name or None if annotation was not "Depend" or "FDepend" annotation

    """
    match = _function_depend_pattern.match(annotation)
    if match is None:
        match = _depend_pattern.match(annotation)

    if match is None:
        return None

    return match.group(3).split(".")[-1]


def _parse_provider_name_from_real_annotation(annotation: Any):
    """Return provider name from annotation.

    Args:
        annotation: Any annotation from param annotation.

    Returns: provider name or None if annotation was not "Depend" or "FDepend" annotation

    """
    annotated: _PAnnotated | None = None
    # case for annotations like "Depend[Foo] | None"
    if is_optional(annotation):
        for _annotation in get_args(annotation):
            if get_origin(_annotation) is Annotated:
                annotated = _annotation
                break
    # case for annotations like "Depend[Foo]"
    elif is_annotated(annotation):
        annotated = annotation

    if annotated is None:
        return None

    args: Sequence[Any] = get_args(annotated)
    # if we have "Depend" annotation get provider name from __args__
    if __DependType__ in args:
        provider = args[0]
    # if we have "FDepend" annotation get provider name from __metadata__
    elif __FDependType__ in args:
        provider = args[1]
    # otherwise return None
    else:
        return None

    # if provider annotation already str just return it
    if isinstance(provider, str):
        return provider

    if isinstance(provider, ForwardRef):
        return provider.__forward_arg__

    # for case when just Depend or FDepend was passed
    if isinstance(provider, TypeVar):
        return None

    # otherwise return provider __name__
    return provider.__name__


def parse_provider_name_from_annotation(annotation: Any) -> None | str:
    """Parse provider name from annotation.

    Args:
        annotation: Any annotation param annotation.

    Returns: provider name or None if annotation was not "Depend" or "FDepend" annotation

    """
    if isinstance(annotation, ForwardRef):
        annotation = annotation.__forward_arg__

    if isinstance(annotation, str):
        # if annotation is str try to get provider name by regexp
        return _parse_provider_name_from_string_annotation(annotation)
    # otherwise try to get provider name from Annotated.__metadata__
    return _parse_provider_name_from_real_annotation(annotation)


def get_signature_parameters_providers(signature: inspect.Signature) -> dict[str, str]:
    """Get function signature parameters dict with providers name.

    Args:
        signature: function signature

    Returns: params dict with providers name

    """
    providers_parameters = {}
    for param in signature.parameters.values():
        provider_name = parse_provider_name_from_annotation(param.annotation)
        if provider_name is None:
            continue

        providers_parameters[param.name] = provider_name

    return providers_parameters
