from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from dep_man import get_django_middleware
from dep_man.core.exceptions import ProviderDoesNotExistsInContextException
from dep_man.integrations.starlette import get_starlette_middleware
from tests.conftest import with_manager
from tests.deps.scopes import Scopes

if TYPE_CHECKING:
    from dep_man.core.managers.bases import DependencyManager
    from dep_man.types import Depend
    from tests.deps.integrations.dependencies import Dep2


def get_call_next(manager: type[DependencyManager], sync: bool, globalize: bool):
    @manager.inject
    class Foo:
        dep2: Depend[Dep2]

    if globalize:

        def call_next(_: Any):
            return Foo().dep2.dep1

    else:

        def call_next(_: Any):
            with manager.inject(Scopes.INTEGRATIONS):
                return Foo().dep2.dep1

    if not sync:
        _call_next = call_next

        async def call_next(_: Any):
            return _call_next(None)

    return call_next


@with_manager("tests.deps.integrations", init=False)
def test_load_deps(manager: type[DependencyManager]):
    assert len(manager.__scopes__) == 1
    assert Scopes.INTEGRATIONS in manager.__scopes__


@with_manager("tests.deps.integrations", init=False)
@pytest.mark.asyncio
async def test_starlet_integration_failure(manager: type[DependencyManager]):
    @manager.inject
    class Foo:
        foo: Depend[Dep2]

    async def call_next(_: Any):
        return Foo().foo

    middleware = get_starlette_middleware(manager, globalize=False)
    with pytest.raises(ProviderDoesNotExistsInContextException) as exc_info:
        await middleware().dispatch(None, call_next)

    assert exc_info.value.name == "Dep2"


@with_manager("tests.deps.integrations", init=False)
@pytest.mark.parametrize("globalize", (True, False))
@pytest.mark.asyncio
async def test_starlet_integration(manager: type[DependencyManager], globalize: bool):
    middleware = get_starlette_middleware(manager, globalize=globalize)
    call_next = get_call_next(manager, sync=False, globalize=globalize)

    from tests.deps.integrations.dependencies import Dep1

    result = await middleware().dispatch(None, call_next)
    assert isinstance(result, Dep1)


@with_manager("tests.deps.integrations", init=False)
@pytest.mark.parametrize("globalize", (True, False))
@pytest.mark.asyncio
async def test_async_django_middleware(manager: type[DependencyManager], globalize: bool):
    middleware = get_django_middleware(manager, globalize=globalize)
    call_next = get_call_next(manager, sync=False, globalize=globalize)

    from tests.deps.integrations.dependencies import Dep1

    result = await middleware(call_next)(None)
    assert isinstance(result, Dep1)


@with_manager("tests.deps.integrations", init=False)
@pytest.mark.parametrize("globalize", (True, False))
def test_sync_django_middleware(manager: type[DependencyManager], globalize: bool):
    middleware = get_django_middleware(manager, globalize=globalize)
    call_next = get_call_next(manager, sync=True, globalize=globalize)

    from tests.deps.integrations.dependencies import Dep1

    result = middleware(call_next)(None)
    assert isinstance(result, Dep1)
