from abc import ABC, abstractmethod
from typing import Protocol

import pytest

from dep_man import DependencyManager
from dep_man.core.exceptions import (
    DependencyAlreadyExistsException,
    InterfaceAlreadyExistsException,
    InterfaceNameOverlapWithProviderException,
    ProviderAlreadyProvidedException,
    ScopeAlreadyExistsException,
)
from tests.conftest import with_manager

scope_name = "new"


@with_manager(init=False)
def test_add_scope(manager: type[DependencyManager]):
    scope = manager.add_scope(scope_name)
    assert scope_name in manager.__scopes__
    assert scope_name == scope.name

    with pytest.raises(ScopeAlreadyExistsException) as exc_info:
        manager.add_scope(scope_name)

    assert exc_info.value.name == scope_name
    assert exc_info.value.manager == manager.__name__


@with_manager(init=False)
def test_functions_scope_provide(manager: type[DependencyManager]):
    scope = manager.add_scope(scope_name)

    class PFunction1(Protocol):
        def __call__(self): ...

    class PFunction2(Protocol):
        def __call__(self): ...

    def function(): ...

    def function_for_export(): ...

    def function_with_interface(): ...

    def function_with_interface_for_export(): ...

    scope.provide(function)
    scope.provide(function_for_export, export=True)
    scope.provide(function_with_interface, interface=PFunction1)
    scope.provide(function_with_interface_for_export, interface=PFunction2, export=True)

    assert function.__mocked_provider__ is True  # type: ignore
    assert function_for_export.__mocked_provider__ is True  # type: ignore
    assert function_with_interface.__mocked_provider__ is True  # type: ignore
    assert function_with_interface_for_export.__mocked_provider__ is True  # type: ignore
    assert not hasattr(PFunction1, "__mocked_provider__")
    assert not hasattr(PFunction2, "__mocked_provider__")

    dependencies = scope._dependencies
    assert dependencies["function"].name == "function"
    assert dependencies["function"].provider == function
    assert dependencies["function"].export is False
    assert dependencies["function"].interface is None

    assert dependencies["function_for_export"].name == "function_for_export"
    assert dependencies["function_for_export"].provider == function_for_export
    assert dependencies["function_for_export"].export is True
    assert dependencies["function_for_export"].interface is None

    assert dependencies["function_with_interface"].name == "function_with_interface"
    assert dependencies["function_with_interface"].provider == function_with_interface
    assert dependencies["function_with_interface"].export is False
    assert dependencies["function_with_interface"].interface is PFunction1

    assert dependencies["function_with_interface_for_export"].name == "function_with_interface_for_export"
    assert dependencies["function_with_interface_for_export"].provider == function_with_interface_for_export
    assert dependencies["function_with_interface_for_export"].export is True
    assert dependencies["function_with_interface_for_export"].interface is PFunction2

    scope.collect()

    assert scope.internal_providers == {
        "function": function,
        "function_with_interface": function_with_interface,
        "function_for_export": function_for_export,
        "function_with_interface_for_export": function_with_interface_for_export,
        "PFunction1": function_with_interface,
        "PFunction2": function_with_interface_for_export,
    }
    assert scope.external_providers == {
        "function_for_export": function_for_export,
        "function_with_interface_for_export": function_with_interface_for_export,
        "PFunction2": function_with_interface_for_export,
    }


@with_manager(init=False)
def test_classes_scope_provide(manager: type[DependencyManager]):
    scope = manager.add_scope(scope_name)

    class IFoo1(ABC):
        @abstractmethod
        def method(self): ...

    class IFoo2(ABC):
        @abstractmethod
        def __call__(self): ...

    class Foo: ...

    class FooForExport: ...

    class FooWithInterface(IFoo1): ...

    class FooWithInterfaceForExport(IFoo2): ...

    scope.provide(Foo)
    scope.provide(FooForExport, export=True)
    scope.provide(FooWithInterface, interface=IFoo1)
    scope.provide(FooWithInterfaceForExport, interface=IFoo2, export=True)

    assert Foo.__dict__["__mocked_provider__"] is True
    assert FooForExport.__dict__["__mocked_provider__"] is True
    assert FooWithInterface.__dict__["__mocked_provider__"] is True
    assert FooWithInterfaceForExport.__dict__["__mocked_provider__"] is True

    assert not hasattr(IFoo1, "__mocked_provider__")
    assert not hasattr(IFoo2, "__mocked_provider__")

    class FooInheritance(Foo): ...

    assert not FooInheritance.__dict__.get("__mocked_provider__")

    scope.provide(FooInheritance)

    assert FooInheritance.__dict__["__mocked_provider__"] is True

    dependencies = scope._dependencies
    assert dependencies["Foo"].name == "Foo"
    assert dependencies["Foo"].provider == Foo
    assert dependencies["Foo"].export is False
    assert dependencies["Foo"].interface is None

    assert dependencies["FooForExport"].name == "FooForExport"
    assert dependencies["FooForExport"].provider == FooForExport
    assert dependencies["FooForExport"].export is True
    assert dependencies["FooForExport"].interface is None

    assert dependencies["FooWithInterface"].name == "FooWithInterface"
    assert dependencies["FooWithInterface"].provider == FooWithInterface
    assert dependencies["FooWithInterface"].export is False
    assert dependencies["FooWithInterface"].interface is IFoo1

    assert dependencies["FooWithInterfaceForExport"].name == "FooWithInterfaceForExport"
    assert dependencies["FooWithInterfaceForExport"].provider == FooWithInterfaceForExport
    assert dependencies["FooWithInterfaceForExport"].export is True
    assert dependencies["FooWithInterfaceForExport"].interface is IFoo2

    assert dependencies["FooInheritance"].name == "FooInheritance"
    assert dependencies["FooInheritance"].provider == FooInheritance
    assert dependencies["FooInheritance"].export is False
    assert dependencies["FooInheritance"].interface is None

    scope.collect()

    assert scope.internal_providers == {
        "Foo": Foo,
        "FooForExport": FooForExport,
        "FooWithInterface": FooWithInterface,
        "FooWithInterfaceForExport": FooWithInterfaceForExport,
        "FooInheritance": FooInheritance,
        "IFoo1": FooWithInterface,
        "IFoo2": FooWithInterfaceForExport,
    }
    assert scope.external_providers == {
        "FooForExport": FooForExport,
        "FooWithInterfaceForExport": FooWithInterfaceForExport,
        "IFoo2": FooWithInterfaceForExport,
    }


@with_manager(init=False)
def test_scope_dependency_already_exists(manager: type[DependencyManager]):
    scope = manager.add_scope(scope_name)

    def foo(): ...

    scope.provide(foo)

    with pytest.raises(DependencyAlreadyExistsException) as exc_info:
        scope.provide(foo)

    assert exc_info.value.name == "foo"
    assert exc_info.value.scope == scope_name


@with_manager(init=False)
def test_scope_interface_already_exists(manager: type[DependencyManager]):
    scope = manager.add_scope(scope_name)

    def interface(): ...
    def foo(): ...
    def bar(): ...

    scope.provide(foo, interface=interface)

    with pytest.raises(InterfaceAlreadyExistsException) as exc_info:
        scope.provide(bar, interface=interface)

    assert exc_info.value.name == "interface"
    assert exc_info.value.scope == scope_name


@with_manager(init=False)
def test_scope_interface_name_overlap_with_provider_exists(manager: type[DependencyManager]):
    scope = manager.add_scope(scope_name)

    def foo(): ...
    def bar(): ...

    scope.provide(foo)

    with pytest.raises(InterfaceNameOverlapWithProviderException) as exc_info:
        scope.provide(bar, interface=foo)

    assert exc_info.value.name == "foo"
    assert exc_info.value.scope == scope_name


@with_manager(init=False)
def test_reprovide(manager: type[DependencyManager]):
    scope1 = manager.add_scope("scope1")
    scope2 = manager.add_scope("scope2")

    def foo(): ...

    scope1.provide(foo)
    with pytest.raises(ProviderAlreadyProvidedException) as exc_info:
        scope2.provide(foo)

    assert exc_info.value.name == "foo"

    class Foo: ...

    scope1.provide(Foo)
    with pytest.raises(ProviderAlreadyProvidedException) as exc_info:
        scope2.provide(Foo)

    assert exc_info.value.name == "Foo"
