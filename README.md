[//]: # (DO NOT CHANGE THIS FILE MANUALLY. Use "make embed-readme" after changing README.template.md file)
<p align="center">
  <img src="docs/resources/brand.svg" width="100%" alt="Web SDK">
</p>
<p align="center">
    <em>Dep man is a dependency manager library with dependency injection implementation and future annotations support for avoiding circular imports.</em>
</p>

<p align="center">

<a href="https://github.com/extralait-web/dep-man/actions?query=event%3Apush+branch%3Amaster+workflow%3ACI" target="_blank">
    <img src="https://img.shields.io/github/actions/workflow/status/extralait-web/dep-man/ci.yml?branch=master&logo=github&label=CI" alt="CI">
</a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/extralait-web/dep-man" target="_blank">
    <img src="https://coverage-badge.samuelcolvin.workers.dev/extralait-web/dep-man.svg" alt="Coverage">
</a>
<a href="https://pypi.python.org/pypi/dep-man-pydi" target="_blank">
    <img src="https://img.shields.io/pypi/v/dep-man-pydi.svg" alt="pypi">
</a>
<a href="https://pepy.tech/project/dep-man-pydi" target="_blank">
    <img src="https://static.pepy.tech/badge/dep-man-pydi/month" alt="downloads">
</a>
<a href="https://github.com/extralait-web/dep-man" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/dep-man-pydi.svg" alt="versions">
</a>
<a href="https://github.com/extralait-web/dep-man" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/extralait-web/dep-man/master/docs/badge/alfa.json" alt="Web SDK alfa">
</a>

</p>

# Installation

Install using `pip install dep-man-pydi` or `uv add dep-man-pydi`

# Features

- [x] ContextVar based injection
- [x] Annotation like providers injection
    - [x] String annotations support
    - [x] ForwardRef annotations support
    - [x] Future annotations support
    - [x] Runtime annotations support
- [x] Scopes support
    - [x] Custom providers scopes
    - [x] Interface based injection from different scopes
    - [x] Multiple scopes context
    - [x] Including other scopes external providers
- [x] Context manager injection
    - [x] Sync manager support
    - [x] Async manager support
    - [x] Nested context managers usage
    - [x] Global context with optional immediate injection
- [x] Classes support
    - [x] Class instances injection
    - [x] Class providers inheritance
    - [x] Nested providers in classes attrs
    - [x] Interface based class instance injection
    - [x] Injection via context manager
    - [x] Injection via global context
    - [x] Mark as injectable via decorating
    - [x] Sync function result attrs injection
    - [x] Async function result attrs injection
- [x] Functions support
    - [x] Sync function result injection
    - [x] Async function result injection
    - [x] Nested providers in function args
    - [x] Protocol based function result injection
    - [x] Injection via context manager
    - [x] Injection via global context
    - [x] Injection via decorating
- [x] Singleton support
    - [x] App level singletons (including any functions results)
    - [ ] Global context singleton support
    - [ ] Current context singleton support
- [x] Dependency manager
    - [x] Multi DI managers support
    - [x] Custom DI managers support
    - [x] DI manager custom Scope type
    - [x] DI manager custom Injector type
- [x] Integrations
    - [x] Django middleware
    - [x] Starlette middleware (can use with FastAPI)

# Examples

```py
# docs/examples/home/minimal/usage.py

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

```
