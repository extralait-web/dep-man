from __future__ import annotations

from typing import TYPE_CHECKING

from tests.consts import FOO_USE_CASE_RESULT
from tests.deps.core.interfaces import IUseCase

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from dep_man.types import Depend, FDepend
    from tests.deps.core.foo.functions import foo_async_arg, foo_sync_arg


class FooObjectArg: ...


class FooOtherObjectArg: ...


class Foo:
    common_attr: bool = True
    object_arg: Depend[FooObjectArg]
    sync_arg: FDepend[str, foo_sync_arg]
    async_arg: FDepend[Awaitable[str], foo_async_arg]


class FooInherited(Foo):
    common_attr: FDepend[str, foo_sync_arg]  # type: ignore
    object_arg: Depend[FooOtherObjectArg]  # type: ignore
    new_sync_arg: FDepend[str, foo_sync_arg]


class FooNested:
    foo: Depend[Foo]


class FooUseCase(IUseCase):
    def execute(self):
        return FOO_USE_CASE_RESULT
