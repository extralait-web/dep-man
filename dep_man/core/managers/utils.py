"""DI Manager Utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dep_man.core.managers.interfaces import IDependencyManager
    from dep_man.types import ProvidersType
    from dep_man.utils.contextvar import SimpleContext, SimpleContextManager


def request_dependencies_context(
    manager: type[IDependencyManager],
) -> SimpleContextManager[SimpleContext[ProvidersType]]:
    """Return simple context manager with dependency manager context."""
    # get current context value
    current_context = manager.__context__.value
    # use context
    return manager.__context__.manager({**current_context})
