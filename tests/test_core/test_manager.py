import pytest

from dep_man import DependencyManager, Scope
from dep_man.core.exceptions import (
    DependencyManagerAlreadyInited,
    DependencyManagerAlreadyLoaded,
    ScopeDoesNotExistsException,
    WrongInjectorTypeException,
    WrongScopeTypeException,
)
from dep_man.core.injectors.bases import Injector
from dep_man.core.managers.bases import BaseDependencyManager
from dep_man.core.managers.interfaces import InitCache
from tests.conftest import with_manager
from tests.deps.scopes import Scopes

packages = ("tests.deps.core.foo", "tests.deps.core.bar")


def test_inheritance_manager():
    class FooManager(BaseDependencyManager): ...

    assert FooManager.__scope_type__ is Scope
    assert FooManager.__injector_type__ is Injector


def test_inheritance_manager_with_alternative_scope():
    class FooScope(Scope): ...

    class FooManager(BaseDependencyManager[FooScope]): ...

    assert FooManager.__scope_type__ is FooScope
    assert FooManager.__injector_type__ is Injector


def test_inheritance_manager_with_alternative_injector():
    class FooInjector(Injector): ...

    class FooManager(BaseDependencyManager[Scope, FooInjector]): ...

    assert FooManager.__scope_type__ is Scope
    assert FooManager.__injector_type__ is FooInjector


def test_inheritance_manager_with_alternative_scope_and_injector():
    class FooScope(Scope): ...

    class FooInjector(Injector): ...

    class FooManager(BaseDependencyManager[FooScope, FooInjector]): ...

    assert FooManager.__scope_type__ is FooScope
    assert FooManager.__injector_type__ is FooInjector


def test_inheritance_manager_with_wrong_scope():
    with pytest.raises(WrongScopeTypeException) as exc_info:

        class FooManager(BaseDependencyManager[int]): ...  # type: ignore

    assert exc_info.value.name == "FooManager"
    assert exc_info.value.value == int.__name__


def test_inheritance_manager_with_wrong_injector():
    with pytest.raises(WrongInjectorTypeException) as exc_info:

        class FooManager(BaseDependencyManager[Scope, int]): ...  # type: ignore

    assert exc_info.value.name == "FooManager"
    assert exc_info.value.value == int.__name__


@with_manager(packages[0], init=False)
def test_load_foo_and_bar_deps(manager):
    assert len(manager.__scopes__) == 1
    assert Scopes.FOO in manager.__scopes__


@with_manager(packages[1], init=False)
def test_load_foo_and_bar_deps(manager):
    assert len(manager.__scopes__) == 1
    assert Scopes.BAR in manager.__scopes__


@with_manager(*packages, init=False)
def test_load_foo_and_bar_deps(manager):
    assert len(manager.__scopes__) == 2
    assert Scopes.FOO in manager.__scopes__
    assert Scopes.BAR in manager.__scopes__


@with_manager(*packages, globalize=True)
def test_fork(manager: type[DependencyManager]):
    new_manager = manager.fork()
    assert new_manager is not manager
    assert new_manager != manager
    assert new_manager.__name__ == f"{manager.__name__}_1"
    assert new_manager.__context__ != manager.__context__
    assert new_manager.__scopes__ == {} != manager.__scopes__
    assert new_manager.__forks_count__ == 0 != manager.__forks_count__
    assert new_manager.__loaded__ is False != manager.__loaded__
    assert new_manager.__inited__ is False != manager.__inited__
    assert new_manager.__init_cache__ == InitCache(providers={}, globalize=False) != manager.__init_cache__

    other_new_manager = new_manager.fork(name="other_new_manager")
    assert other_new_manager.__name__ == "other_new_manager"


@with_manager(*packages, init=False)
def test_provide(manager: type[DependencyManager]):
    def test_foo(): ...

    manager.provide(test_foo, scope=Scopes.FOO)
    assert "test_foo" in manager.__scopes__[Scopes.FOO]._dependencies

    not_existed_scope = "not_existed_scope"
    with pytest.raises(ScopeDoesNotExistsException) as exc_info:
        manager.provide(test_foo, scope=not_existed_scope)

    assert exc_info.value.name == not_existed_scope
    assert exc_info.value.manager == manager.__name__


@with_manager(*packages, init=False)
def test_reload_without_flag(manager: type[DependencyManager]):
    with pytest.raises(DependencyManagerAlreadyLoaded) as exc_info:
        manager.load()

    assert exc_info.value.name == manager.__name__


@with_manager(*packages)
def test_reinit(manager: type[DependencyManager]):
    new_provider = "NewProvider"

    manager.__init_cache__["providers"][new_provider] = new_provider
    manager.init()
    assert manager.__init_cache__["providers"][new_provider] == new_provider

    manager.init(reinit=True)
    assert new_provider not in manager.__init_cache__["providers"]

    with pytest.raises(DependencyManagerAlreadyInited) as exc_info:
        manager.init(globalize=True)

    assert exc_info.value.name == manager.__name__


@with_manager(*packages)
def test_injector_exit_without_enter(manager: type[DependencyManager]):
    assert manager.inject(Scopes.FOO).__exit__(None, None, None) is False
