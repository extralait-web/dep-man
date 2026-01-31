"""Module for working with contextvars."""

from __future__ import annotations

import uuid
from contextvars import ContextVar, Token
from typing import TYPE_CHECKING, Generic, cast

from dep_man.types import T
from dep_man.utils.exceptions import ExceptionModel

if TYPE_CHECKING:
    from collections.abc import Callable


class ContextAlreadyActive(RuntimeError, ExceptionModel):
    """Raised when a provider not present in context."""

    name: str

    __template__ = "{name} is already active."


class ContextNotActive(RuntimeError, ExceptionModel):
    """Raised when a provider not present in context."""

    name: str

    __template__ = "{name} is not active."


class SimpleContextManager(Generic[T]):
    """Context manager for SimpleContext.

    Notes:
        This code adopted from python-with-contextvars (https://github.com/bob1de/python-with-contextvars/blob/main/with_contextvars.py).

    """

    __slots__ = ("_context", "_value", "_token")

    _context: SimpleContext[T]
    """Simple context instance"""
    _value: T | None
    """ContextVar value"""
    _token: Token | None
    """ContextVar token"""

    def __init__(self, context: SimpleContext[T], value: T):
        """Set context variables with new values."""
        self._context = context
        self._value = value
        self._token = None

    def __enter__(self):
        """Enter in context."""
        if self._token is not None:
            raise ContextAlreadyActive(name=str(self))
        # set new value and save _token for reset old state
        self._token = self._context.context.set(self._value)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit from context."""
        if self._token is None:
            raise ContextNotActive(name=str(self))

        # reset old state from token
        self._token.var.reset(self._token)
        self._token = None

    def __repr__(self):
        """Represent context variables as a string."""
        return "<{module}.{qualname} ({status}) : {var}={value}>".format(
            module=type(self).__module__,
            qualname=type(self).__qualname__,
            status="active" if self.is_active else "inactive",
            var=self._context.context.name,
            value=self._value,
        )

    @property
    def is_active(self) -> bool:
        """Whether this context manager is currently active."""
        return self._token is not None


class SimpleContext(Generic[T]):
    """Class for creating a simple context through contextvars.ContextVar."""

    _default: T | None
    _default_factory: Callable[[], T] | None
    _context: ContextVar[T | None]
    _initialized: bool

    def __init__(self, default: T | None = None, default_factory: Callable[[], T] | None = None):
        """Initialize with default values.

        Args:
            default: default value
            default_factory: default value factory
        """
        self._default = default
        self._default_factory = default_factory

        self._context = ContextVar(uuid.uuid4().hex)
        self._initialized = False

    def __init_context__(self, value: T | None = None) -> None:
        """Initialize context variable value."""
        if value is not None:
            self._context.set(value)
        elif self._default_factory:
            self.context.set(self._default_factory())
        else:
            self.context.set(self._default)
        self._initialized = True

    @property
    def context(self) -> ContextVar[T | None]:
        """Context variable value."""
        return self._context

    @property
    def value(self) -> T:
        """Return context variable value."""
        if not self._initialized:
            self.__init_context__()

        return cast("T", self.context.get())

    def manager(self, value) -> SimpleContextManager[SimpleContext[T]]:
        """Return context manager for simple context."""
        return SimpleContextManager(self, value)  # type: ignore
