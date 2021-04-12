from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence

T = TypeVar('T')


class Renderer(Generic[T], ABC):
    @abstractmethod
    def render(self) -> T:
        raise NotImplementedError('abstract method')


class SequenceRenderer(Generic[T], ABC):
    @abstractmethod
    def render_sequence(self) -> Sequence[T]:
        raise NotImplementedError('abstract method')
