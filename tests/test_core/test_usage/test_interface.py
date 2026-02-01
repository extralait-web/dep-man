from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from dep_man.core.exceptions import ProviderDoesNotExistsInContextException
from tests.conftest import with_manager
from tests.consts import (
    BAR_USE_CASE_RESULT,
    FOO_USE_CASE_RESULT,
    PACKAGES,
)
from tests.deps.scopes import Scopes

if TYPE_CHECKING:
    from dep_man import DependencyManager
    from dep_man.types import Depend
    from tests.deps.core.interfaces import IUseCase


@with_manager(*PACKAGES)
def test_interface_in_different_scopes(manager: type[DependencyManager]):
    @manager.inject
    class FooWithInterface:
        use_case: Depend[IUseCase]

        def execute(self):
            return self.use_case.execute()

    with pytest.raises(ProviderDoesNotExistsInContextException):
        FooWithInterface().execute()

    with manager.inject(Scopes.FOO):
        assert FooWithInterface().execute() == FOO_USE_CASE_RESULT

    with manager.inject(Scopes.BAR):
        assert FooWithInterface().execute() == BAR_USE_CASE_RESULT

    with manager.inject(Scopes.FOO):
        assert FooWithInterface().execute() == FOO_USE_CASE_RESULT

        with manager.inject(Scopes.BAR):
            assert FooWithInterface().execute() == BAR_USE_CASE_RESULT

    with manager.inject(Scopes.BAR):
        assert FooWithInterface().execute() == BAR_USE_CASE_RESULT

        with manager.inject(Scopes.FOO):
            assert FooWithInterface().execute() == FOO_USE_CASE_RESULT
