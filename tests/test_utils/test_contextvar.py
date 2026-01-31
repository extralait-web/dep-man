import pytest

from dep_man.utils.contextvar import ContextAlreadyActive, ContextNotActive, SimpleContext


def test_simple_context_initialized():
    ctx1 = SimpleContext()
    assert ctx1._initialized is False
    ctx1.__init_context__()
    assert ctx1._initialized is True

    ctx2 = SimpleContext()
    assert ctx2._initialized is False

    ctx2.value
    assert ctx2._initialized is True


def test_simple_context_default():
    default_value = 1

    ctx1 = SimpleContext[int](default=default_value)
    assert ctx1.value == default_value

    default_factory = lambda: default_value

    ctx2 = SimpleContext[int](default_factory=default_factory)
    assert ctx2.value == default_value


def test_simple_context_reinit():
    default_value = 1

    ctx = SimpleContext[int](default=default_value)
    assert ctx.value == default_value

    new_value = 2
    ctx.__init_context__(new_value)
    assert ctx.value == new_value


def test_simple_context_manager():
    default_value = 1

    ctx = SimpleContext[int](default=default_value)
    assert ctx.value == default_value

    new_value = 2
    with ctx.manager(new_value):
        assert ctx.value == new_value

    assert ctx.value == default_value


def test_simple_context_manager_nested_context():
    default_value = 1

    ctx = SimpleContext[int](default=default_value)
    assert ctx.value == default_value

    new_value = 2
    with ctx.manager(new_value):
        assert ctx.value == new_value

        nested_value = 3
        with ctx.manager(nested_value):
            assert ctx.value == nested_value

        assert ctx.value == new_value

    assert ctx.value == default_value


def test_simple_context_manager_repeat_call():
    ctx = SimpleContext[int](default=True)

    manager = ctx.manager(False)

    with pytest.raises(ContextAlreadyActive):
        with manager:
            with manager:
                ...


def test_simple_context_exit_without_token():
    ctx = SimpleContext[int](default=True)

    with pytest.raises(ContextNotActive):
        ctx.manager(False).__exit__(None, None, None)
