from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import ContextManager, Iterator, IO, Optional

from exactly_lib.impls.types.string_model.contents_handler.handler_with_cached_path import \
    ContentsHandlerWithCachedPathFromWriteTo
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class Writer(ABC):
    @abstractmethod
    def write(self, tmp_file_space: DirFileSpace, output: IO):
        pass


class ContentsHandlerViaWriteTo(ContentsHandlerWithCachedPathFromWriteTo):
    def __init__(self,
                 tmp_file_space: DirFileSpace,
                 writer: Writer,
                 file_name: Optional[str] = None,
                 ):
        super().__init__(file_name)
        self.__tmp_file_space = tmp_file_space
        self._writer = writer

    @property
    def as_str(self) -> str:
        with self.as_file.open() as f:
            return f.read()

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self.as_file.open() as lines:
            yield lines

    def write_to(self, output: IO):
        self._writer.write(self.__tmp_file_space, output)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space
