from abc import ABC
from typing import TypeVar, Generic

T = TypeVar('T')


class Renderer(Generic[T], ABC):
    def render(self) -> T:
        pass
