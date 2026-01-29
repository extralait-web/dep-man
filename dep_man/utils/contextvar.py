"""Module for working with contextvars."""

from __future__ import annotations

import uuid
from contextvars import ContextVar, Token, copy_context
from copy import deepcopy
from functools import partial, wraps
from typing import TYPE_CHECKING, Generic, Literal, TypeAlias, cast, overload

from typing_extensions import Self

from dep_man.types import R, T

if TYPE_CHECKING:
    from collections.abc import Callable

AtomicContextModes: TypeAlias = Literal["init", "copy", "share"]


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
            raise RuntimeError(f"{self} is already active")
        self._token = self._context.context.set(self._value)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit from context."""
        if self._token is None:
            raise RuntimeError(f"{self} is not active")

        self._token.var.reset(self._token)
        self._token = None

    def __repr__(self):
        """Represent context variables as a string."""
        return "<{module}.{qualname} ({status}) : {var}={value}>".format(
            module=type(self).__module__,
            qualname=type(self).__qualname__,
            status="inactive" if self._token is None else "active",
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

    def __copy_from__(self, other: Self):
        """Copy context variable value."""
        self.context.set(deepcopy(other.value))

    @property
    def context(self) -> ContextVar[T | None]:
        """Context variable value."""
        return self._context

    @property
    def initialized(self):
        """Return True if the context is initialized."""
        return self._initialized

    @property
    def value(self) -> T:
        """Return context variable value."""
        if not self._initialized:
            self.__init_context__()

        return cast("T", self.context.get())

    @overload
    def atomic_context(
        self,
        function: Callable[..., R],
        mode: AtomicContextModes = "init",
    ) -> Callable[..., R]: ...
    @overload
    def atomic_context(
        self,
        function: None = None,
        mode: AtomicContextModes = "init",
    ) -> Callable[[Callable[..., R]], Callable[..., R]]: ...
    def atomic_context(
        self,
        function: Callable[..., R] | None = None,
        mode: AtomicContextModes = "init",
    ) -> Callable[..., R] | Callable[[Callable[..., R]], Callable[..., R]]:
        """Atomic context during function execution.

        Args:
            function: function for execution in atomic context
            mode: Atomic context mode
                init: The parent context will not change, and the initial value of the context will
                      be the same as when it was first initialized
                copy: The parent context will not change, and the initial value of the context will
                      be the same as the parent
                share: The parent context can change if it is a mutable data type, and the initial
                      value of the context will be the same as the parent

        Returns: passed function or current method

        """
        if not function:
            return partial(self.atomic_context, mode=mode)

        @wraps(function)
        def wrapper(*args, **kwargs) -> R:
            context = copy_context()

            def _function() -> R:
                if mode == "init":
                    self.__init_context__()
                elif mode == "copy":
                    self.__copy_from__(self)
                return function(*args, **kwargs)

            return context.run(_function)

        return wrapper
