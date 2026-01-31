import pytest

from dep_man import DependencyManager
from tests.conftest import with_manager
from tests.consts import PACKAGES
from tests.deps.scopes import Scopes


@with_manager(*PACKAGES)
def test_sync_context_access(manager: type[DependencyManager]):
    from tests.deps.core.bar.functions import bar_sync_arg
    from tests.deps.core.foo.functions import foo_sync_arg

    assert bar_sync_arg.__name__ not in manager.__context__.value
    assert foo_sync_arg.__name__ not in manager.__context__.value

    with manager.inject(Scopes.FOO):
        assert foo_sync_arg.__name__ in manager.__context__.value
        assert bar_sync_arg.__name__ not in manager.__context__.value
        with manager.inject(Scopes.BAR):
            assert foo_sync_arg.__name__ in manager.__context__.value
            assert bar_sync_arg.__name__ in manager.__context__.value

        assert foo_sync_arg.__name__ in manager.__context__.value
        assert bar_sync_arg.__name__ not in manager.__context__.value

    assert bar_sync_arg.__name__ not in manager.__context__.value
    assert foo_sync_arg.__name__ not in manager.__context__.value

    with manager.inject(Scopes.BAR):
        assert foo_sync_arg.__name__ not in manager.__context__.value
        assert bar_sync_arg.__name__ in manager.__context__.value
        with manager.inject(Scopes.FOO):
            assert foo_sync_arg.__name__ in manager.__context__.value
            assert bar_sync_arg.__name__ in manager.__context__.value

        assert foo_sync_arg.__name__ not in manager.__context__.value
        assert bar_sync_arg.__name__ in manager.__context__.value

    assert bar_sync_arg.__name__ not in manager.__context__.value
    assert foo_sync_arg.__name__ not in manager.__context__.value

    with manager.inject(Scopes.FOO, Scopes.BAR):
        assert foo_sync_arg.__name__ in manager.__context__.value
        assert bar_sync_arg.__name__ in manager.__context__.value

    assert bar_sync_arg.__name__ not in manager.__context__.value
    assert foo_sync_arg.__name__ not in manager.__context__.value


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_context_access(manager: type[DependencyManager]):
    from tests.deps.core.bar.functions import bar_sync_arg
    from tests.deps.core.foo.functions import foo_sync_arg

    assert bar_sync_arg.__name__ not in manager.__context__.value
    assert foo_sync_arg.__name__ not in manager.__context__.value

    async with manager.inject(Scopes.FOO):
        assert foo_sync_arg.__name__ in manager.__context__.value
        assert bar_sync_arg.__name__ not in manager.__context__.value
        async with manager.inject(Scopes.BAR):
            assert foo_sync_arg.__name__ in manager.__context__.value
            assert bar_sync_arg.__name__ in manager.__context__.value

        assert foo_sync_arg.__name__ in manager.__context__.value
        assert bar_sync_arg.__name__ not in manager.__context__.value

    assert bar_sync_arg.__name__ not in manager.__context__.value
    assert foo_sync_arg.__name__ not in manager.__context__.value

    async with manager.inject(Scopes.BAR):
        assert foo_sync_arg.__name__ not in manager.__context__.value
        assert bar_sync_arg.__name__ in manager.__context__.value
        async with manager.inject(Scopes.FOO):
            assert foo_sync_arg.__name__ in manager.__context__.value
            assert bar_sync_arg.__name__ in manager.__context__.value
        assert foo_sync_arg.__name__ not in manager.__context__.value
        assert bar_sync_arg.__name__ in manager.__context__.value

    assert bar_sync_arg.__name__ not in manager.__context__.value
    assert foo_sync_arg.__name__ not in manager.__context__.value

    async with manager.inject(Scopes.FOO, Scopes.BAR):
        assert foo_sync_arg.__name__ in manager.__context__.value
        assert bar_sync_arg.__name__ in manager.__context__.value

    assert bar_sync_arg.__name__ not in manager.__context__.value
    assert foo_sync_arg.__name__ not in manager.__context__.value


@with_manager(*PACKAGES)
def test_export(manager: type[DependencyManager]):
    from tests.deps.core.bar.functions import bar_export, bar_sync_arg

    with manager.inject(Scopes.FOO):
        assert bar_sync_arg.__name__ not in manager.__context__.value
        assert bar_export.__name__ in manager.__context__.value
