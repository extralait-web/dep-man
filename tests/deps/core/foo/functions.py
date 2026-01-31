from __future__ import annotations

from typing import TYPE_CHECKING

from dep_man.types import BIND
from tests.consts import FOO_ASYNC_ARG_RESULT, FOO_SYNC_ARG_RESULT

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from dep_man.types import Depend, FDepend
    from tests.deps.core.foo.classes import FooObjectArg


def foo_sync_arg():
    return FOO_SYNC_ARG_RESULT


async def foo_async_arg():
    return FOO_ASYNC_ARG_RESULT


def foo_sync(
    common_arg: bool = False,
    sync_arg: FDepend[str, foo_sync_arg] = BIND,
    *,
    common_kwarg: bool = False,
    object_arg: Depend[FooObjectArg] = BIND,
):
    return common_arg, sync_arg, common_kwarg, object_arg


async def foo_async(
    common_arg: bool = False,
    sync_arg: FDepend[str, foo_sync_arg] = BIND,
    async_arg: FDepend[Awaitable[str], foo_async_arg] = BIND,
    *,
    common_kwarg: bool = False,
    object_arg: Depend[FooObjectArg] = BIND,
):
    return common_arg, sync_arg, await async_arg, common_kwarg, object_arg


async def foo_nested(foo: FDepend[Awaitable[tuple], foo_async] = BIND):
    return await foo
