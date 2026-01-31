from dep_man import dm
from tests.deps.core.foo.classes import (
    Foo,
    FooInherited,
    FooNested,
    FooObjectArg,
    FooOtherObjectArg,
    FooUseCase,
)
from tests.deps.core.foo.functions import (
    foo_async,
    foo_async_arg,
    foo_nested,
    foo_sync,
    foo_sync_arg,
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
