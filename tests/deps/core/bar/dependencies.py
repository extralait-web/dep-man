from dep_man import dm
from tests.deps.core.bar.classes import BarUseCase
from tests.deps.core.bar.functions import bar_export, bar_sync_arg
from tests.deps.core.interfaces import IUseCase
from tests.deps.scopes import Scopes

scope = dm.add_scope(Scopes.BAR, include=(Scopes.FOO,))
scope.provide(bar_sync_arg)
scope.provide(bar_export, export=True)
scope.provide(BarUseCase, interface=IUseCase)
