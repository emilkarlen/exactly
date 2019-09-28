from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence

from exactly_lib.type_system.trace.trace import Detail, Node


class DetailsRenderer(ABC):
    @abstractmethod
    def render(self) -> Sequence[Detail]:
        pass


NODE_DATA = TypeVar('NODE_DATA')


class NodeRenderer(Generic[NODE_DATA], ABC):
    @abstractmethod
    def render(self) -> Node[NODE_DATA]:
        pass
