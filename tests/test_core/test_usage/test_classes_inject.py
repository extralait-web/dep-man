from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from dep_man.core.exceptions import ClassBaseInjectionContextDoesNotSupport, ProviderDoesNotExistsInContextException
from dep_man.types import BIND, Depend, FDepend
from tests.conftest import with_manager
from tests.consts import (
    BAR_EXPORT_RESULT,
    BAR_SYNC_ARG_RESULT,
    BAR_USE_CASE_RESULT,
    FOO_ASYNC_ARG_RESULT,
    FOO_SYNC_ARG_RESULT,
    FOO_USE_CASE_RESULT,
    PACKAGES,
)
from tests.deps.scopes import Scopes

if TYPE_CHECKING:
    from dep_man import DependencyManager
    from tests.deps.core.bar.functions import bar_export, bar_sync_arg
    from tests.deps.core.foo.classes import Foo
    from tests.deps.core.foo.functions import foo_sync_arg
    from tests.deps.core.interfaces import IUseCase


def _get_foo_inject(manager: type[DependencyManager]):
    @manager.inject
    class FooInject:
        foo: Depend[Foo]

    return FooInject()


@with_manager(*PACKAGES)
def test_sync_contex_inject_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo, FooObjectArg

    foo_inject = _get_foo_inject(manager)

    with manager.inject(Scopes.FOO):
        assert isinstance(foo_inject.foo, Foo)
        assert foo_inject.foo.common_attr is True
        assert isinstance(foo_inject.foo.object_arg, FooObjectArg)
        assert foo_inject.foo.sync_arg == FOO_SYNC_ARG_RESULT


@with_manager(*PACKAGES, globalize=(Scopes.FOO,))
def test_sync_global_context_inject_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo, FooObjectArg

    foo_inject = _get_foo_inject(manager)

    assert isinstance(foo_inject.foo, Foo)
    assert foo_inject.foo.common_attr is True
    assert isinstance(foo_inject.foo.object_arg, FooObjectArg)
    assert foo_inject.foo.sync_arg == FOO_SYNC_ARG_RESULT


@with_manager(*PACKAGES)
def test_sync_no_context_inject_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo

    with pytest.raises(ProviderDoesNotExistsInContextException) as exc_info:
        foo_inject = _get_foo_inject(manager)
        foo_inject.foo

    assert exc_info.value.name == Foo.__name__


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_context_inject_class(manager: type[DependencyManager]):
    foo_inject = _get_foo_inject(manager)

    with manager.inject(Scopes.FOO):
        assert await foo_inject.foo.async_arg == FOO_ASYNC_ARG_RESULT


@with_manager(*PACKAGES, globalize=(Scopes.FOO,))
@pytest.mark.asyncio
async def test_async_global_context_class(manager: type[DependencyManager]):
    foo_inject = _get_foo_inject(manager)

    assert await foo_inject.foo.async_arg == FOO_ASYNC_ARG_RESULT


@with_manager(*PACKAGES)
@pytest.mark.asyncio
async def test_async_no_context_class(manager: type[DependencyManager]):
    from tests.deps.core.foo.classes import Foo

    with pytest.raises(ProviderDoesNotExistsInContextException) as exc_info:
        foo_inject = _get_foo_inject(manager)
        foo_inject.foo

    assert exc_info.value.name == Foo.__name__


@with_manager(*PACKAGES)
def test_class_base_injection_cotext(manager: type[DependencyManager]):
    with pytest.raises(ClassBaseInjectionContextDoesNotSupport) as exc_info:

        @manager.inject(Scopes.FOO)
        class FooInject:
            foo: Depend[Foo]

    assert exc_info.value.name == "FooInject"

    with pytest.raises(ClassBaseInjectionContextDoesNotSupport) as exc_info:

        class FooInject:
            foo: Depend[Foo]

        manager.inject(FooInject, Scopes.FOO)

    assert exc_info.value.name == "FooInject"


@with_manager(*PACKAGES)
def test_class_methods(manager: type[DependencyManager]):
    @manager.inject
    class Foo:
        use_case: Depend[IUseCase]

        @manager.inject(Scopes.FOO)
        def method(self, arg: bool, depend: FDepend[str, foo_sync_arg] = BIND):
            return arg, depend

        @staticmethod
        @manager.inject(Scopes.BAR)
        def static_method(arg: bool, depend: FDepend[str, bar_sync_arg] = BIND):
            return arg, depend

        @classmethod
        @manager.inject(Scopes.FOO)
        def class_method(cls, arg: bool, depend: FDepend[str, bar_export] = BIND):
            return arg, depend

    foo_no_context = Foo()
    assert foo_no_context.method(True) == (True, FOO_SYNC_ARG_RESULT)
    assert foo_no_context.static_method(True) == (True, BAR_SYNC_ARG_RESULT)
    assert foo_no_context.class_method(True) == (True, BAR_EXPORT_RESULT)

    with manager.inject(Scopes.FOO):
        from pprint import pprint

        pprint(manager.__context__.value)

        foo_foo_context = Foo()

        assert foo_foo_context.use_case.execute() == FOO_USE_CASE_RESULT
        assert foo_foo_context.method(True) == (True, FOO_SYNC_ARG_RESULT)
        assert foo_foo_context.static_method(True) == (True, BAR_SYNC_ARG_RESULT)
        assert foo_foo_context.class_method(True) == (True, BAR_EXPORT_RESULT)

        with manager.inject(Scopes.BAR):
            pprint(manager.__context__.value)

            foo_bar_context = Foo()

            assert foo_foo_context.use_case.execute() == FOO_USE_CASE_RESULT

            assert foo_bar_context.use_case.execute() == BAR_USE_CASE_RESULT
            assert foo_bar_context.method(True) == (True, FOO_SYNC_ARG_RESULT)
            assert foo_bar_context.static_method(True) == (True, BAR_SYNC_ARG_RESULT)
            assert foo_bar_context.class_method(True) == (True, BAR_EXPORT_RESULT)


@with_manager(*PACKAGES)
def test_interface_in_different_scopes(manager: type[DependencyManager]):
    @manager.inject
    class FooWithInterface:
        use_case: Depend[IUseCase]

        def execute(self):
            return self.use_case.execute()

    with pytest.raises(ProviderDoesNotExistsInContextException):
        FooWithInterface().execute()

    with manager.inject(Scopes.FOO):
        assert FooWithInterface().execute() == FOO_USE_CASE_RESULT

    with manager.inject(Scopes.BAR):
        assert FooWithInterface().execute() == BAR_USE_CASE_RESULT

    with manager.inject(Scopes.FOO):
        assert FooWithInterface().execute() == FOO_USE_CASE_RESULT

        with manager.inject(Scopes.BAR):
            assert FooWithInterface().execute() == BAR_USE_CASE_RESULT

    with manager.inject(Scopes.BAR):
        assert FooWithInterface().execute() == BAR_USE_CASE_RESULT

        with manager.inject(Scopes.FOO):
            assert FooWithInterface().execute() == FOO_USE_CASE_RESULT
