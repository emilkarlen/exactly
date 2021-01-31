from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, TextIO

from exactly_lib.impls.types.string_source.contents.contents_with_cached_path import \
    StringSourceContentsWithCachedPath
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class FileCreator(ABC):
    @abstractmethod
    def create(self, tmp_file_space: DirFileSpace) -> Path:
        pass


class ContentsViaFile(StringSourceContentsWithCachedPath):
    def __init__(self,
                 tmp_file_space: DirFileSpace,
                 file_creator: FileCreator,
                 ):
        super().__init__()
        self.__tmp_file_space = tmp_file_space
        self._file_creator = file_creator

    @property
    def may_depend_on_external_resources(self) -> bool:
        return True

    @property
    def as_str(self) -> str:
        with self.as_file.open() as f:
            return f.read()

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self.as_file.open() as lines:
            yield lines

    def write_to(self, output: TextIO):
        with self.as_file.open() as lines:
            output.writelines(lines)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space

    def _to_file(self) -> Path:
        return self._file_creator.create(self.tmp_file_space)
