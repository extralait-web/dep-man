import pytest

from dep_man import DependencyManager
from tests.conftest import with_manager
from tests.consts import FOO_ASYNC_ARG_RESULT, FOO_SYNC_ARG_RESULT, PACKAGES
from tests.deps.scopes import Scopes


@with_manager(*PACKAGES)
def test_sync_context_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg
    from tests.deps.core.foo.functions import foo_sync

    assert foo_sync.__name__ not in manager.__context__.value

    with manager.inject(Scopes.FOO):
        assert foo_sync.__name__ in manager.__context__.value

        common_arg, sync_arg, common_kwarg, object_arg = foo_sync(True, common_kwarg=True)
        assert common_arg is True
        assert sync_arg == FOO_SYNC_ARG_RESULT
        assert common_kwarg is True
        assert isinstance(object_arg, FooObjectArg)


@with_manager(*PACKAGES)
def test_sync_nested_context_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg
    from tests.deps.core.foo.functions import foo_sync

    assert foo_sync.__name__ not in manager.__context__.value

    with manager.inject(Scopes.BAR):
        assert foo_sync.__name__ not in manager.__context__.value

        with manager.inject(Scopes.FOO):
            assert foo_sync.__name__ in manager.__context__.value

            common_arg, sync_arg, common_kwarg, object_arg = foo_sync(True, common_kwarg=True)
            assert common_arg is True
            assert sync_arg == FOO_SYNC_ARG_RESULT
            assert common_kwarg is True
            assert isinstance(object_arg, FooObjectArg)


@with_manager(*PACKAGES)
def test_sync_no_context_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg
    from tests.deps.core.foo.functions import foo_sync

    assert foo_sync.__name__ not in manager.__context__.value

    common_arg, sync_arg, common_kwarg, object_arg = foo_sync(True, common_kwarg=True)
    assert common_arg is True
    assert sync_arg == FOO_SYNC_ARG_RESULT
    assert common_kwarg is True
    assert isinstance(object_arg, FooObjectArg)


@with_manager(*PACKAGES, globalize=(Scopes.FOO,))
def test_sync_global_context_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg
    from tests.deps.core.foo.functions import foo_sync

    assert foo_sync.__name__ in manager.__context__.value

    common_arg, sync_arg, common_kwarg, object_arg = foo_sync(True, common_kwarg=True)
    assert common_arg is True
    assert sync_arg == FOO_SYNC_ARG_RESULT
    assert common_kwarg is True
    assert isinstance(object_arg, FooObjectArg)


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_context_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg
    from tests.deps.core.foo.functions import foo_async

    assert foo_async.__name__ not in manager.__context__.value

    async with manager.inject(Scopes.FOO):
        assert foo_async.__name__ in manager.__context__.value

        common_arg, sync_arg, async_arg, common_kwarg, object_arg = await foo_async(True, common_kwarg=True)
        assert common_arg is True
        assert sync_arg == FOO_SYNC_ARG_RESULT
        assert async_arg == FOO_ASYNC_ARG_RESULT
        assert common_kwarg is True
        assert isinstance(object_arg, FooObjectArg)


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_nested_async_context_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg
    from tests.deps.core.foo.functions import foo_async

    assert foo_async.__name__ not in manager.__context__.value

    async with manager.inject(Scopes.BAR):
        assert foo_async.__name__ not in manager.__context__.value

        async with manager.inject(Scopes.FOO):
            assert foo_async.__name__ in manager.__context__.value

            common_arg, sync_arg, async_arg, common_kwarg, object_arg = await foo_async(True, common_kwarg=True)
            assert common_arg is True
            assert sync_arg == FOO_SYNC_ARG_RESULT
            assert async_arg == FOO_ASYNC_ARG_RESULT
            assert common_kwarg is True
            assert isinstance(object_arg, FooObjectArg)


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_no_context_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg
    from tests.deps.core.foo.functions import foo_async

    assert foo_async.__name__ not in manager.__context__.value

    common_arg, sync_arg, async_arg, common_kwarg, object_arg = await foo_async(True, common_kwarg=True)
    assert common_arg is True
    assert sync_arg == FOO_SYNC_ARG_RESULT
    assert async_arg == FOO_ASYNC_ARG_RESULT
    assert common_kwarg is True
    assert isinstance(object_arg, FooObjectArg)


@with_manager(*PACKAGES, globalize=(Scopes.FOO,))
@pytest.mark.asyncio
async def test_async_global_context_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg
    from tests.deps.core.foo.functions import foo_async

    assert foo_async.__name__ in manager.__context__.value

    common_arg, sync_arg, async_arg, common_kwarg, object_arg = await foo_async(True, common_kwarg=True)
    assert common_arg is True
    assert sync_arg == FOO_SYNC_ARG_RESULT
    assert async_arg == FOO_ASYNC_ARG_RESULT
    assert common_kwarg is True
    assert isinstance(object_arg, FooObjectArg)


@with_manager(*PACKAGES, globalize=(Scopes.FOO,))
@pytest.mark.asyncio
async def test_nested_function(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooObjectArg
    from tests.deps.core.foo.functions import foo_nested

    common_arg, sync_arg, async_arg, common_kwarg, object_arg = await foo_nested()
    assert common_arg is False
    assert sync_arg == FOO_SYNC_ARG_RESULT
    assert async_arg == FOO_ASYNC_ARG_RESULT
    assert common_kwarg is False
    assert isinstance(object_arg, FooObjectArg)
