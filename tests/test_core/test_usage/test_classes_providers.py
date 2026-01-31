import pytest

from dep_man import DependencyManager
from tests.conftest import with_manager
from tests.consts import FOO_ASYNC_ARG_RESULT, FOO_SYNC_ARG_RESULT, PACKAGES
from tests.deps.scopes import Scopes


@with_manager(*PACKAGES)
def test_sync_context_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo, FooObjectArg

    assert Foo.__name__ not in manager.__context__.value

    with manager.inject(Scopes.FOO):
        assert Foo.__name__ in manager.__context__.value

        foo = Foo()
        assert foo.common_attr is True
        assert isinstance(foo.object_arg, FooObjectArg)
        assert foo.sync_arg == FOO_SYNC_ARG_RESULT


@with_manager(*PACKAGES)
def test_sync_nested_context_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo, FooObjectArg

    assert Foo.__name__ not in manager.__context__.value

    with manager.inject(Scopes.BAR):
        assert Foo.__name__ not in manager.__context__.value

        with manager.inject(Scopes.FOO):
            assert Foo.__name__ in manager.__context__.value

            foo = Foo()
            assert foo.common_attr is True
            assert isinstance(foo.object_arg, FooObjectArg)
            assert foo.sync_arg == FOO_SYNC_ARG_RESULT


@with_manager(*PACKAGES)
def test_sync_no_context_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo, FooObjectArg

    assert Foo.__name__ not in manager.__context__.value

    foo = Foo()
    assert foo.common_attr is True
    assert isinstance(foo.object_arg, FooObjectArg)
    assert foo.sync_arg == FOO_SYNC_ARG_RESULT


@with_manager(*PACKAGES, globalize=(Scopes.FOO,))
def test_sync_global_context_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo, FooObjectArg

    assert Foo.__name__ in manager.__context__.value

    foo = Foo()
    assert foo.common_attr is True
    assert isinstance(foo.object_arg, FooObjectArg)
    assert foo.sync_arg == FOO_SYNC_ARG_RESULT


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_context_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo

    assert Foo.__name__ not in manager.__context__.value

    with manager.inject(Scopes.FOO):
        assert Foo.__name__ in manager.__context__.value

        foo = Foo()
        assert (await foo.async_arg) == FOO_ASYNC_ARG_RESULT


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_nested_context_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo

    assert Foo.__name__ not in manager.__context__.value

    with manager.inject(Scopes.BAR):
        assert Foo.__name__ not in manager.__context__.value

        with manager.inject(Scopes.FOO):
            assert Foo.__name__ in manager.__context__.value

            foo = Foo()
            assert (await foo.async_arg) == FOO_ASYNC_ARG_RESULT


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_no_context_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo

    assert Foo.__name__ not in manager.__context__.value

    foo = Foo()
    assert (await foo.async_arg) == FOO_ASYNC_ARG_RESULT


@with_manager(*PACKAGES, globalize=(Scopes.FOO,))
@pytest.mark.asyncio
async def test_async_global_context_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo

    assert Foo.__name__ in manager.__context__.value

    foo = Foo()
    assert (await foo.async_arg) == FOO_ASYNC_ARG_RESULT


@with_manager(*PACKAGES, globalize=(Scopes.FOO,))
@pytest.mark.asyncio
async def test_inheritance_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import FooInherited, FooOtherObjectArg

    foo = FooInherited()
    assert foo.common_attr == FOO_SYNC_ARG_RESULT
    assert isinstance(foo.object_arg, FooOtherObjectArg)
    assert foo.sync_arg == FOO_SYNC_ARG_RESULT
    assert foo.new_sync_arg == FOO_SYNC_ARG_RESULT
    assert (await foo.async_arg) == FOO_ASYNC_ARG_RESULT


@with_manager(*PACKAGES, globalize=(Scopes.FOO,))
@pytest.mark.asyncio
async def test_nested_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo, FooNested, FooObjectArg

    foo_nested = FooNested()
    assert isinstance(foo_nested.foo, Foo)
    assert foo_nested.foo.common_attr is True
    assert isinstance(foo_nested.foo.object_arg, FooObjectArg)
    assert foo_nested.foo.sync_arg == FOO_SYNC_ARG_RESULT
    assert (await foo_nested.foo.async_arg) == FOO_ASYNC_ARG_RESULT
