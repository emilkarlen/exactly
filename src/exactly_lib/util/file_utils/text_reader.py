from abc import ABC, abstractmethod
from typing import TextIO


class TextFromFileReader(ABC):
    @abstractmethod
    def read(self, f: TextIO) -> str:
        pass
