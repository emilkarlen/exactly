from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import ContextManager, Iterator, Optional, TextIO

from exactly_lib.impls.types.string_source.contents.contents_with_cached_path import \
    ContentsWithCachedPathFromWriteToBase
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class Writer(ABC):
    @abstractmethod
    def write(self, tmp_file_space: DirFileSpace, output: TextIO):
        pass


class ContentsViaWriteTo(ContentsWithCachedPathFromWriteToBase):
    def __init__(self,
                 tmp_file_space: DirFileSpace,
                 writer: Writer,
                 file_name: Optional[str] = None,
                 ):
        super().__init__(file_name)
        self._tmp_file_space = tmp_file_space
        self._writer = writer

    @property
    def may_depend_on_external_resources(self) -> bool:
        return True

    @property
    def as_str(self) -> str:
        with self.as_file.open() as f:
            ret_val = f.read()
        return ret_val

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self.as_file.open() as lines:
            yield lines

    def write_to(self, output: TextIO):
        if self._as_file_path is not None:
            with self._as_file_path.open() as f_cached:
                output.writelines(f_cached)
        else:
            self._writer.write(self._tmp_file_space, output)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._tmp_file_space
