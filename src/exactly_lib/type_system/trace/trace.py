from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic

RET = TypeVar('RET')


class Detail(ABC):
    @abstractmethod
    def accept(self, visitor: 'DetailVisitor[RET]') -> RET:
        pass


class StringDetail(Detail):
    """A detail that is a string without any special structure."""

    def __init__(self, string: str):
        self._string = string

    def accept(self, visitor: 'DetailVisitor[RET]') -> RET:
        return visitor.visit_string(self)

    @property
    def string(self) -> str:
        return self._string


class DetailVisitor(Generic[RET], ABC):
    @abstractmethod
    def visit_string(self, x: StringDetail) -> RET:
        pass


NODE_DATA = TypeVar('NODE_DATA')


class Node(Generic[NODE_DATA]):
    def __init__(self,
                 header: str,
                 data: NODE_DATA,
                 details: Sequence[Detail],
                 children: Sequence['Node[NODE_DATA]']):
        self._header = header
        self._data = data
        self._details = details
        self._children = children

    @property
    def header(self) -> str:
        return self._header

    @property
    def data(self) -> NODE_DATA:
        return self._data

    @property
    def details(self) -> Sequence[Detail]:
        return self._details

    @property
    def children(self) -> Sequence['Node[NODE_DATA]']:
        return self._children
