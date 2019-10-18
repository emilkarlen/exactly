from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence

T = TypeVar('T')


class Renderer(Generic[T], ABC):
    @abstractmethod
    def render(self) -> T:
        pass


class SequenceRenderer(Generic[T], ABC):
    @abstractmethod
    def render_sequence(self) -> Sequence[T]:
        pass
