from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.conftest import with_manager
from tests.consts import (
    PACKAGES,
)
from tests.deps.scopes import Scopes

if TYPE_CHECKING:
    from dep_man import DependencyManager


@with_manager(*PACKAGES)
def test_class_singleton(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooNotSingleton, FooSingleton

    with manager.inject(Scopes.FOO):
        assert FooSingleton() is FooSingleton()
        assert FooNotSingleton() is not FooNotSingleton()


@with_manager(*PACKAGES)
def test_sync_function_singleton(manager: type[DependencyManager]):
    from tests.deps.core.foo.functions import foo_sync_not_singleton, foo_sync_singleton

    with manager.inject(Scopes.FOO):
        assert foo_sync_singleton() is foo_sync_singleton()
        assert foo_sync_not_singleton() is not foo_sync_not_singleton()


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_function_singleton(manager: type[DependencyManager]):
    from tests.deps.core.foo.functions import foo_async_not_singleton, foo_async_singleton

    async with manager.inject(Scopes.FOO):
        assert await foo_async_singleton() is await foo_async_singleton()
        assert await foo_async_not_singleton() is not await foo_async_not_singleton()
