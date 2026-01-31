from dep_man.utils.builtins import copy_func


def test_copy_func():
    default_value = 0
    value = 1

    def foo(a: int = default_value, *, b: int = default_value):
        return a, b

    new_foo = copy_func(foo)

    assert foo is not new_foo
    assert foo != new_foo

    assert foo() == new_foo() == (default_value, default_value)
    assert foo(a=value, b=value) == foo(a=value, b=value) == (value, value)
    assert foo.__defaults__ == new_foo.__defaults__ == (default_value,)
    assert foo.__kwdefaults__ == new_foo.__kwdefaults__ == {"b": default_value}

    new_foo.__defaults__ = (value,)
    new_foo.__kwdefaults__ = {"b": value}

    assert foo() == (default_value, default_value)
    assert new_foo() == (value, value)
