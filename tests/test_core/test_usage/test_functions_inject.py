from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from dep_man.core.exceptions import ProviderDoesNotExistsInContextException
from dep_man.types import BIND, FDepend
from tests.conftest import with_manager
from tests.consts import (
    BAR_SYNC_ARG_RESULT,
    FOO_ASYNC_ARG_RESULT,
    FOO_SYNC_ARG_RESULT,
    PACKAGES,
)
from tests.test_core.test_manager import Scopes

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from dep_man import DependencyManager
    from tests.deps.core.foo.functions import foo_async, foo_sync, foo_sync_arg


@with_manager(*PACKAGES)
def test_sync_inject_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg

    @manager.inject(Scopes.FOO)
    def foo_inject(args: FDepend[tuple, foo_sync] = BIND):
        return args

    common_arg, sync_arg, common_kwarg, object_arg = foo_inject()
    assert common_arg is False
    assert sync_arg == FOO_SYNC_ARG_RESULT
    assert common_kwarg is False
    assert isinstance(object_arg, FooObjectArg)


@with_manager(*PACKAGES)
def test_sync_no_inject_function(manager: type[DependencyManager]):
    def foo_inject(args: FDepend[tuple, foo_sync] = BIND):
        return args

    assert BIND == foo_inject()


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_inject_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg

    @manager.inject(Scopes.FOO)
    async def foo_inject(args: FDepend[Awaitable[tuple], foo_async] = BIND):
        return await args

    common_arg, sync_arg, async_arg, common_kwarg, object_arg = await foo_inject()

    assert common_arg is False
    assert sync_arg == FOO_SYNC_ARG_RESULT
    assert async_arg == FOO_ASYNC_ARG_RESULT
    assert common_kwarg is False
    assert isinstance(object_arg, FooObjectArg)


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_no_inject_function(manager: type[DependencyManager]):
    async def foo_inject(args: FDepend[Awaitable[tuple], foo_async] = BIND):
        return args

    assert BIND == await foo_inject()


@with_manager(*PACKAGES)
def test_function_inject_without_scope(manager: type[DependencyManager]):
    from tests.deps.core.bar.functions import bar_sync_arg
    from tests.deps.core.foo.functions import foo_sync_arg

    assert bar_sync_arg.__name__ not in manager.__context__.value
    assert foo_sync_arg.__name__ not in manager.__context__.value

    @manager.inject
    def foo_inject(bar: FDepend[str, bar_sync_arg] = BIND, foo: FDepend[str, foo_sync_arg] = BIND):
        assert bar == BAR_SYNC_ARG_RESULT
        assert foo == FOO_SYNC_ARG_RESULT

    foo_inject()


@with_manager(*PACKAGES)
def test_function_dynamic_inject_without_certain_scope(manager: type[DependencyManager]):
    from tests.deps.core.bar.functions import bar_sync_arg
    from tests.deps.core.foo.functions import foo_sync_arg

    assert bar_sync_arg.__name__ not in manager.__context__.value
    assert foo_sync_arg.__name__ not in manager.__context__.value

    def foo_inject(bar: FDepend[str, bar_sync_arg] = BIND, foo: FDepend[str, foo_sync_arg] = BIND):
        assert bar == BAR_SYNC_ARG_RESULT
        assert foo == FOO_SYNC_ARG_RESULT

    manager.inject(foo_inject, Scopes.FOO)

    with pytest.raises(ProviderDoesNotExistsInContextException) as exc_info:
        foo_inject()

    assert exc_info.value.name == bar_sync_arg.__name__
