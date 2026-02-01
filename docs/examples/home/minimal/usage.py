from collections.abc import Awaitable

from dep_man import BIND, Depend, FDepend, dm


# declare sync function
def foo() -> str:
    return "foo_value"


# declare async function
async def async_foo() -> str:
    return "async_foo_value"


# declare function with dependence on foo
def bar(foo_value: FDepend[str, foo] = BIND) -> tuple[str, str]:
    # also you can use Depend and FDepend with function or classes
    # which also hame save annotations their values will be created
    # from context or scope providers
    return "bar_value", foo_value


# declare interface
class IFoo:
    foo: bool
    var: int


# declare class with dependence on foo and bar
class Foo(IFoo):
    # in this case all fields with "Depend" of "FDepend" annotations
    # will be replaced with descriptor for getting value from context
    foo: FDepend[bool, foo]
    bar: FDepend[int, bar]
    # also you can use Depend and FDepend with function or classes
    # which also hame save annotations their values will be created
    # from context or scope providers

    # inheritance providers is also supported


# declare function for providing singleton result
def singleton(arg: Depend[Foo] = BIND) -> Foo:
    return arg


# I recommend creating a new scopes and call provide methods
# in the "dependencies.py" file in the roots of your modules or applications

# as scope name you can use Enum or str
scope = dm.add_scope("scope")
# provide functions and classes
scope.provide(foo)
scope.provide(async_foo)
scope.provide(bar)
# provide Foo with interface, you can use Depend[Foo] or Depend[IFoo] for getting Foo instance
scope.provide(Foo, interface=IFoo)
# singleton result function

# you can also provide object in certain scope using dm method
dm.provide(singleton, scope="scope", singleton=True)


# declare class with interface for other scope
class OtherFoo(IFoo):
    foo = False
    bar = -1


# create other scope
other_scope = dm.add_scope("other_scope")
# provide class in other scope with same interface
other_scope.provide(OtherFoo, interface=IFoo)

# next you need specify modules for loading
# if you have next structure
"""
...
├── app
└   ├── bar
    │   ├── ...
    │   ├── dependencies.py
    │   ├── __init__.py
    └── foo
        ├── ...
        ├── dependencies.py
        ├── __init__.py
"""

# you need make next load call
dm.load("app.bar", "app.foo")

# you can also specify file_name via load arg file_name
dm.load("app.bar", "app.foo", file_name="your_file")

# for django you need call this in ready method of you AppConfig
dm.load()

# at the beginning of the request you need call dm.init()
# if you use starlette, fastapy or django you can use middleware
from dep_man import get_django_middleware, get_starlette_middleware

# this method you need call for every request in middleware
dm.init()
# you can use globalize=True for add providers from all scopes globally to dm context
dm.init(globalize=True)
# or add to global context only certain scopes
dm.init(globalize=("notifications", "settings"))


# if you use context of run dm.init(globalize=True)
# you can create instance or call functions for any provider
# without context manager usage
foo_instance = Foo()  # <__main__.Foo object at ...>
foo_instance.foo  # 'foo_value'
foo_instance.bar  # ('bar_value', 'foo_value')

# singleton function result
singleton() is singleton()  # True


# If you want to inject dependencies into a class that was not provided,
# use need decorate this class with dm.inject as decorator
@dm.inject
class Injectable:
    # in this case all fields with "Depend" of "FDepend" annotations
    # will be replaced with descriptor for getting value from context
    foo: Depend[Foo]
    foo_from_interface: Depend[IFoo]


# usage example via context manager
with dm.inject("scope"):
    # create instance of inject decorated class
    instance = Injectable()

    # Foo instance was created ones and set to instance.__dict__
    instance.foo  # <__main__.Foo object at ...>

    instance.foo_from_interface  # <__main__.Foo object at ...>

    # foo call ones for getting result and set to instance.__dict__
    instance.foo.foo  # foo_value

    # bar call ones for getting result and set to instance.__dict__
    # inside the bar call foo was called once.
    instance.foo.bar  # ('bar_value', 'foo_value')


# you can also use nested context managers
with dm.inject("scope"):
    instance = Injectable()
    # In this context we will get the provider instance with interface=IFoo from the scope
    isinstance(instance.foo_from_interface, Foo)  # True

    with dm.inject("other_scope"):
        instance = Injectable()
        # In this context we will get the provider instance with interface=IFoo from the other_scope
        isinstance(instance.foo_from_interface, OtherFoo)  # True


# usage example via function decoration
# here you can specify scopes or inject all if not specify
@dm.inject("scope")
def injectable(common: bool, arg: Depend[Foo] = BIND):
    # in this case injectable __code__ will be replaced passing
    # providers via signature.parameters defaults values from context
    return common, arg.foo, arg.bar


# function call will be run with dm.inject("scope") context
injectable(True)  # (True, 'foo_value', ('bar_value', 'foo_value'))


# async support logic of the injector's operation is similar
@dm.inject
class Foo:
    # you can add async function result to you instances attrs
    async_attr: FDepend[Awaitable[bool], async_foo]


# you can use async variant of context manager
async with dm.inject("scope"):
    async with dm.inject("other_scope"):
        # you can get async function result from provider
        await Foo().async_attr  # async_foo_value


# you can use inject decorator on async function
@dm.inject("scope")
async def async_injectable(common: bool, arg: FDepend[Awaitable[bool], async_foo] = BIND):
    return common, await arg


await async_injectable(common=True)  # (True, 'async_foo_value')
