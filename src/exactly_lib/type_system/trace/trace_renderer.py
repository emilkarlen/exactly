from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.type_system.trace.trace import Detail, Node


class DetailRenderer(ABC):
    @abstractmethod
    def render(self) -> Detail:
        pass


NODE_DATA = TypeVar('NODE_DATA')


class NodeRenderer(Generic[NODE_DATA], ABC):
    @abstractmethod
    def render(self) -> Node[NODE_DATA]:
        pass
