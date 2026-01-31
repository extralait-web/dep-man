import re
import sys

import pytest

from dep_man import dm
from dep_man.consts import DEFAULT_DEPENDENCIES_FILE_NAME
from dep_man.core.managers.bases import DependencyManager
from dep_man.types import ScopeNameType


@pytest.fixture()
def manager(mocker, request) -> type[DependencyManager]:
    packages, file_name, reload, globalize, reinit, init = request.param

    manager = dm.fork()
    mocker.patch("dep_man.dm", new=manager)

    for package in packages:
        # we need clean all modules for reinit
        package = f"{package}.{file_name}" if file_name else package
        parent_package = package.rsplit(".", 1)[0]

        pattern = re.compile(rf"{parent_package}*")
        modules_to_delete = [module for module in sys.modules if pattern.match(module)]
        for module in modules_to_delete:
            del sys.modules[module]

    manager.load(*packages, file_name=file_name, reload=reload)
    if init:
        manager.init(globalize, reinit=reinit)
    return manager


def with_manager(
    *packages,
    file_name: str | None = DEFAULT_DEPENDENCIES_FILE_NAME,
    reload: bool = False,
    init: bool = True,
    globalize: bool | tuple[ScopeNameType] = False,
    reinit: bool = False,
):
    return pytest.mark.parametrize("manager", [[packages, file_name, reload, globalize, reinit, init]], indirect=True)
