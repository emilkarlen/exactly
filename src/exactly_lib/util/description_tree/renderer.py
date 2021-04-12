from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence

from exactly_lib.util.description_tree.tree import Detail, Node


class DetailsRenderer(ABC):
    @abstractmethod
    def render(self) -> Sequence[Detail]:
        raise NotImplementedError('abstract method')


NODE_DATA = TypeVar('NODE_DATA')


class NodeRenderer(Generic[NODE_DATA], ABC):
    @abstractmethod
    def render(self) -> Node[NODE_DATA]:
        raise NotImplementedError('abstract method')
