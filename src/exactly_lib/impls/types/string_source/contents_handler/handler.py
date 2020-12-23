from abc import ABC, abstractmethod
from pathlib import Path
from typing import ContextManager, Iterator, IO

from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class ContentsHandler(ABC):
    """
    Handles the variants of the contents of a :class:`StringSource`

    Each method correspond to one of :class:`StringSource`.
    """

    @property
    @abstractmethod
    def may_depend_on_external_resources(self) -> bool:
        pass

    @property
    @abstractmethod
    def as_str(self) -> str:
        pass

    @property
    @abstractmethod
    def as_file(self) -> Path:
        pass

    @property
    @abstractmethod
    def as_lines(self) -> ContextManager[Iterator[str]]:
        pass

    @abstractmethod
    def write_to(self, output: IO):
        pass

    @property
    @abstractmethod
    def tmp_file_space(self) -> DirFileSpace:
        pass
