from abc import ABC
from typing import Sequence, TypeVar, Generic


class Detail(ABC):
    pass


NODE_DATA = TypeVar('NODE_DATA')


class Node(Generic[NODE_DATA]):
    def __init__(self,
                 header: str,
                 data: NODE_DATA,
                 details: Sequence[Detail],
                 children: Sequence['Node']):
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


class StringDetail(Detail):
    """A detail that is a string without any special structure."""

    def __init__(self, string: str):
        self._string = string

    @property
    def string(self) -> str:
        return self._string
