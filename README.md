[//]: # (DO NOT CHANGE THIS FILE MANUALLY. Use "make embed-readme" after changing README.template.md file)
<p align="center">
  <img src="docs/resources/brand.svg" width="100%" alt="Web SDK">
</p>
<p align="center">
    <em>Dep man is a dependency manager library with dependency injection implementation and future annotations supporting for avoiding circular imports.</em>
</p>

<p align="center">

<a href="https://github.com/extralait-web/dep-man/actions?query=event%3Apush+branch%3Amaster+workflow%3ACI" target="_blank">
    <img src="https://img.shields.io/github/actions/workflow/status/extralait-web/dep-man/ci.yml?branch=master&logo=github&label=CI" alt="CI">
</a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/extralait-web/dep-man" target="_blank">
    <img src="https://coverage-badge.samuelcolvin.workers.dev/extralait-web/dep-man.svg" alt="Coverage">
</a>
<a href="https://pypi.python.org/pypi/dep-man" target="_blank">
    <img src="https://img.shields.io/pypi/v/dep-man.svg" alt="pypi">
</a>
<a href="https://pepy.tech/project/dep-man" target="_blank">
    <img src="https://static.pepy.tech/badge/dep-man/month" alt="downloads">
</a>
<a href="https://github.com/extralait-web/dep-man" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/dep-man.svg" alt="versions">
</a>
<a href="https://github.com/extralait-web/dep-man" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/extralait-web/dep-man/master/docs/badge/alfa.json" alt="Web SDK alfa">
</a>

</p>

# Installation

Install using `pip install dep-man-pydi` or `uv add dep-man-pydi`

# Features

- [x] Annotation like providers injection
- [x] Future annotation support
- [x] Class instances injection
- [x] Sync and Async function result injection
- [x] Nested providers for inject in classes attrs and function args
- [x] Classes providers inheritance
- [x] ContextVar based injection
- [x] Scopes with grouped providers
- [x] Export providers in other scopes
- [x] Interfaces and protocol based injection from different scopes
- [x] Sync and Async context manager like injection
- [x] Nested context managers usage
- [x] Global context for avoiding context manager usage
- [x] Decoration like scopes injection for functions
- [x] Decoration like injection for classes
- [x] Middlewares for django and starlette
- [x] Multi DI managers supporting
- [x] Supported custom DI managers, scopes and injectors classes

# Examples

```py
# docs/examples/home/minimal/usage.py

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

```
