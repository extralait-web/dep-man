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
- [x] Singleton supporting
    - [x] App level singletons (including any functions results)
    - [ ] Global context singleton support
    - [ ] Current context singleton support
- [x] Dependency manager
    - [x] Multi DI managers supporting
    - [x] Custom DI managers supporting
    - [x] DI manager custom Scope type
    - [x] DI manager custom Injector type
- [x] Integrations
    - [x] Django middleware
    - [x] Starlet middleware (can use with FastAPI)

# Examples

```py
# docs/examples/home/minimal/usage.py
```
