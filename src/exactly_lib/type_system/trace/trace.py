from abc import ABC
from typing import Sequence


class Detail(ABC):
    pass


class Node:
    def __init__(self,
                 header: str,
                 details: Sequence[Detail],
                 children: Sequence['Node']):
        self._header = header
        self._details = details
        self._children = children

    @property
    def header(self) -> str:
        return self._header

    @property
    def details(self) -> Sequence[Detail]:
        return self._details

    @property
    def children(self) -> Sequence['Node']:
        return self._children


class StringDetail(Detail):
    """A detail that is a string without any special structure."""

    def __init__(self, string: str):
        self._string = string

    @property
    def string(self) -> str:
        return self._string
