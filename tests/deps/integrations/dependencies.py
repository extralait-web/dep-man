from dep_man import dm
from dep_man.types import Depend
from tests.deps.scopes import Scopes


class Dep1: ...


class Dep2:
    dep1: Depend[Dep1]


scope = dm.add_scope(Scopes.INTEGRATIONS)
scope.provide(Dep1)
scope.provide(Dep2)
