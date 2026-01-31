from abc import ABC, abstractmethod
from typing import Any, Protocol


class PInterfaceFunction(Protocol):
    def __call__(self): ...


class IUseCase(ABC):
    @abstractmethod
    def execute(self) -> Any: ...
