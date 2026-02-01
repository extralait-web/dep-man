from dep_man import dm
from tests.deps.core.foo.classes import (
    Foo,
    FooInherited,
    FooNested,
    FooNotSingleton,
    FooObjectArg,
    FooOtherObjectArg,
    FooSingleton,
    FooUseCase,
)
from tests.deps.core.foo.functions import (
    foo_async,
    foo_async_arg,
    foo_async_not_singleton,
    foo_async_singleton,
    foo_nested,
    foo_sync,
    foo_sync_arg,
    foo_sync_not_singleton,
    foo_sync_singleton,
)
from tests.deps.core.interfaces import IUseCase
from tests.deps.scopes import Scopes

scope = dm.add_scope(Scopes.FOO, include=(Scopes.BAR,))
scope.provide(foo_sync_arg)
scope.provide(foo_async_arg)
scope.provide(foo_sync)
scope.provide(foo_async)
scope.provide(foo_nested)
scope.provide(Foo)
scope.provide(FooObjectArg)
scope.provide(FooOtherObjectArg)
scope.provide(FooInherited)
scope.provide(FooNested)
scope.provide(FooUseCase, interface=IUseCase)
scope.provide(FooNotSingleton)
scope.provide(FooSingleton, singleton=True)
scope.provide(foo_sync_not_singleton)
scope.provide(foo_sync_singleton, singleton=True)
scope.provide(foo_async_not_singleton)
scope.provide(foo_async_singleton, singleton=True)
