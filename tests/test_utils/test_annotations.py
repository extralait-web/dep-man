import inspect
from collections.abc import Awaitable
from typing import Annotated, Any, ForwardRef, Optional

import pytest

from dep_man.types import Depend, FDepend, T
from dep_man.utils.annotations import (
    _parse_provider_name_from_real_annotation,
    _parse_provider_name_from_string_annotation,
    get_signature_parameters_providers,
    is_annotated,
    is_optional,
    parse_provider_name_from_annotation,
)


class Provider: ...


class __PDepend__: ...


PDepend = Annotated[T, __PDepend__]
PFDepend = Annotated


def function_provider(): ...


@pytest.mark.parametrize(
    "annotation,result",
    [
        (Depend[bool], False),
        (Depend[bool] | None, True),
        (None | Depend[bool], True),
        (None | Depend[bool] | None, True),
        (FDepend[bool, bool], False),
        (FDepend[bool, bool] | None, True),  # pyright: ignore [reportOperatorIssue]
        (None | FDepend[bool, bool], True),  # pyright: ignore [reportOperatorIssue]
        (None | FDepend[bool, bool] | None, True),  # pyright: ignore [reportOperatorIssue]
    ],
)
def test_is_optional(annotation: Any, result: bool):
    assert is_optional(annotation) == result


def test_is_annotated():
    assert is_annotated(Depend[bool])
    assert is_annotated(FDepend[bool, bool])
    assert not is_annotated(bool)
    assert not is_annotated(bool | None)


string_annotations = [
    ("Depend[Provider]", "Provider"),
    ("Depend[Provider] | None", "Provider"),
    ("None | Depend[Provider]", "Provider"),
    ("None | Depend[Provider] | None", "Provider"),
    ("Optional[Depend[Provider]]", "Provider"),
    ("Optional[FDepend[bool, function_provider]]", "function_provider"),
    ("FDepend[bool, function_provider]", "function_provider"),
    ("FDepend[bool, function_provider] | None", "function_provider"),
    ("FDepend[bool, function_provider]", "function_provider"),
    ("FDepend[bool | None, function_provider] | None", "function_provider"),
    ("FDepend[dict[str, dict[str, Any]], function_provider] | None", "function_provider"),
    ("FDepend[dict[str, dict[str, Any]] | None, function_provider] | None", "function_provider"),
    ("FDepend[Awaitable[bool], function_provider] | None", "function_provider"),
    ("FDepend[Awaitable[bool | None], function_provider] | None", "function_provider"),
    ("FDepend[Awaitable[dict[str, dict[str, Any]]], function_provider] | None", "function_provider"),
    ("FDepend[Awaitable[dict[str, dict[str, Any]]] | None, function_provider] | None", "function_provider"),
    ("Depend[some.path.Provider]", "Provider"),
    ("FDepend[bool, some.path.function_provider]", "function_provider"),
    # Negative
    ("bool", None),
    ("Depend", None),
    ("FDepend", None),
    ("PDepend[Provider]", None),
    ("PDepend[Provider] | None", None),
    ("None | PDepend[Provider]", None),
    ("None | PDepend[Provider] | None", None),
    ("Optional", None),
    ("Optional[PDepend[Provider]]", None),
    ("Optional[PFDepend[bool, function_provider]]", None),
    ("PFDepend[bool, function_provider]", None),
    ("PFDepend[bool, function_provider] | None", None),
    ("PFDepend[bool, function_provider]", None),
    ("PFDepend[bool | None, function_provider] | None", None),
    ("PFDepend[dict[str, dict[str, Any]], function_provider] | None", None),
    ("PFDepend[dict[str, dict[str, Any]] | None, function_provider] | None", None),
    ("PFDepend[Awaitable[bool], function_provider] | None", None),
    ("PFDepend[Awaitable[bool | None], function_provider] | None", None),
    ("PFDepend[Awaitable[dict[str, dict[str, Any]]], function_provider] | None", None),
    ("PFDepend[Awaitable[dict[str, dict[str, Any]]] | None, function_provider] | None", None),
]

real_annotations = [
    (Depend["Provider"], "Provider"),
    (Depend[Provider], "Provider"),
    (Depend[Provider] | None, "Provider"),
    (None | Depend[Provider], "Provider"),
    (None | Depend[Provider] | None, "Provider"),
    (Optional[Depend[Provider]], "Provider"),  # noqa
    (Optional[FDepend[bool, function_provider]], "function_provider"),  # noqa
    (FDepend[bool, "function_provider"], "function_provider"),
    (FDepend[bool, function_provider], "function_provider"),
    (FDepend[bool, function_provider] | None, "function_provider"),  # pyright: ignore [reportOperatorIssue]
    (FDepend[bool, function_provider], "function_provider"),  # pyright: ignore [reportOperatorIssue]
    (FDepend[bool | None, function_provider] | None, "function_provider"),  # pyright: ignore [reportOperatorIssue]
    (FDepend[dict[str, dict[str, Any]], function_provider] | None, "function_provider"),  # pyright: ignore [reportOperatorIssue]
    (FDepend[dict[str, dict[str, Any]] | None, function_provider] | None, "function_provider"),  # pyright: ignore [reportOperatorIssue]
    (FDepend[Awaitable[bool], function_provider] | None, "function_provider"),  # pyright: ignore [reportOperatorIssue]
    (FDepend[Awaitable[bool | None], function_provider] | None, "function_provider"),  # pyright: ignore [reportOperatorIssue]
    (FDepend[Awaitable[dict[str, dict[str, Any]]], function_provider] | None, "function_provider"),  # pyright: ignore [reportOperatorIssue]
    (FDepend[Awaitable[dict[str, dict[str, Any]]] | None, function_provider] | None, "function_provider"),  # pyright: ignore [reportOperatorIssue]
    # negative
    (bool, None),
    (Depend, None),
    (FDepend, None),
    (PDepend[Provider], None),
    (PDepend[Provider] | None, None),
    (None | PDepend[Provider], None),
    (None | PDepend[Provider] | None, None),
    (Optional, None),
    (Optional[PDepend[Provider]], None),  # noqa
    (Optional[PFDepend[bool, function_provider]], None),  # noqa
    (PFDepend[bool, function_provider], None),
    (PFDepend[bool, function_provider] | None, None),  # pyright: ignore [reportOperatorIssue]
    (PFDepend[bool, function_provider], None),  # pyright: ignore [reportOperatorIssue]
    (PFDepend[bool | None, function_provider] | None, None),  # pyright: ignore [reportOperatorIssue]
    (PFDepend[dict[str, dict[str, Any]], function_provider] | None, None),  # pyright: ignore [reportOperatorIssue]
    (PFDepend[dict[str, dict[str, Any]] | None, function_provider] | None, None),  # pyright: ignore [reportOperatorIssue]
    (PFDepend[Awaitable[bool], function_provider] | None, None),  # pyright: ignore [reportOperatorIssue]
    (PFDepend[Awaitable[bool | None], function_provider] | None, None),  # pyright: ignore [reportOperatorIssue]
    (PFDepend[Awaitable[dict[str, dict[str, Any]]], function_provider] | None, None),  # pyright: ignore [reportOperatorIssue]
    (PFDepend[Awaitable[dict[str, dict[str, Any]]] | None, function_provider] | None, None),  # pyright: ignore [reportOperatorIssue]
]

forward_annotations = [
    (ForwardRef("Depend[Provider]"), "Provider"),
    (ForwardRef("FDepend[bool, function_provider]"), "function_provider"),
    (ForwardRef("Depend[some.path.Provider]"), "Provider"),
    (ForwardRef("FDepend[bool, some.path.function_provider]"), "function_provider"),
]


@pytest.mark.parametrize("annotation,result", string_annotations)
def test_parse_provider_name_from_string_annotation(annotation: str, result: bool):
    assert _parse_provider_name_from_string_annotation(annotation) == result


@pytest.mark.parametrize("annotation,result", real_annotations)
def test_parse_provider_name_from_real_annotation(annotation: Any, result: bool):
    assert _parse_provider_name_from_real_annotation(annotation) == result


@pytest.mark.parametrize("annotation,result", [*string_annotations, *real_annotations, *forward_annotations])
def test_provider_name_from_annotation(annotation: Any, result: bool):
    assert parse_provider_name_from_annotation(annotation) == result


def test_get_signature_parameters_providers():
    def function(
        a: Provider,
        a_provider: Depend[Provider],
        /,
        b: bool,
        b_provider: FDepend[bool, function_provider],
        c: bool = False,
        c_provider: FDepend[bool, function_provider] = False,
        *args: Any,
        d: Provider,
        d_provider: Depend[Provider],
        e: Provider | None = None,
        e_provider: Depend[Provider] | None = None,
        **kwargs: Any,
    ): ...

    signature = inspect.signature(function)
    parameters_providers = get_signature_parameters_providers(signature)

    assert parameters_providers["a_provider"] == "Provider"
    assert parameters_providers["b_provider"] == "function_provider"
    assert parameters_providers["c_provider"] == "function_provider"
    assert parameters_providers["d_provider"] == "Provider"
    assert parameters_providers["e_provider"] == "Provider"
    assert "a" not in parameters_providers
    assert "b" not in parameters_providers
    assert "c" not in parameters_providers
    assert "d" not in parameters_providers
    assert "e" not in parameters_providers
