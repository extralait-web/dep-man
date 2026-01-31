from typing import Awaitable

from dep_man import dm
from dep_man.types import BIND, Depend, FDepend


# declare function for providing in any file
def foo() -> str:
    return "foo_value"


# declare function with dependence on foo
def bar(foo_value: FDepend[str, foo] = BIND) -> tuple[str, str]:
    # also you can use Depend and FDepend with function or classes
    # which also hame save annotations their values will be created
    # from context or scope providers
    return "bar_value", foo_value


# declare class with dependence on foo and bar
class Foo:
    # in this case all fields with "Depend" of "FDepend" annotations
    # will be replaced with descriptor for getting value from context
    foo: FDepend[bool, foo]
    bar: FDepend[int, bar]
    # also you can use Depend and FDepend with function or classes
    # which also hame save annotations their values will be created
    # from context or scope providers

    # inheritance providers is also supported


# I recommend creating a new scope in the "dependencies.py" file
# in the roots of your modules or applications,
# and adding providers there as well
scope = dm.add_scope("scope")
# provide functions and classes
scope.provide(foo)
scope.provide(bar)
scope.provide(Foo)

"""
next you need specify modules for loading

if you have next structure
--
├── app
└   ├── bar
    │   ├── ...
    │   ├── dependencies.py
    │   ├── __init__.py
    └── foo
        ├── ...
        ├── dependencies.py
        ├── __init__.py

you need make next load call
dm.load(
    "core.bar",
    "core.foo",
)

you can also specify file_name via load arg file_name
"""

# for django you need call this in ready method of you AppConfig
dm.load()

# this method you need call for every request in middleware
dm.init()


# use injector on class object
@dm.inject
class Injectable:
    # in this case all fields with "Depend" of "FDepend" annotations
    # will be replaced with descriptor for getting value from context
    foo: Depend[Foo]


# usage example via context manager
with dm.inject("scope"):
    # create instance of inject decorated class
    instance = Injectable()

    # Foo instance was created ones and set to instance.__dict__
    instance.foo
    # <__main__.Foo object at ...>

    # foo call ones for getting result and set to instance.__dict__
    instance.foo.foo
    # foo_value

    # bar call ones for getting result and set to instance.__dict__
    # inside the bar call foo was called once.
    instance.foo.bar
    # ('bar_value', 'foo_value')

    # if you use context of run dm.init(globalize=True)
    # you can create instance or call functions for any provider
    foo_instance = Foo()
    foo_instance.foo
    # foo_value
    foo_instance.bar
    # ('bar_value', 'foo_value')


# you can also use nested context managers
with dm.inject("scope1"):
    with dm.inject("scope2"):
        with dm.inject("scope3"):
            pass


# via function decoration
# here you can specify scope or inject all if not specify
@dm.inject("scope")
def injectable(arg: Depend[Foo] = BIND):
    # in this case injectable __code__ will be replaced passing
    # providers via signature.parameters defaults values from context
    return arg.foo, arg.bar


# function call will be run with dm.inject("scope") context
injectable()
# ('foo_value', ('bar_value', 'foo_value'))


# async support
@dm.inject
class Foo:
    async_arg: FDepend[Awaitable[bool], async_func]


async with dm.inject("scope1"):
    async with dm.inject("scope2"):
        await Foo().async_arg


@dm.inject("scope")
async def async_injectable(arg: FDepend[Awaitable[bool], async_func]):
    return await arg
