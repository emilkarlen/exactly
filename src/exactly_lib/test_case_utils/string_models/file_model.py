from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator

from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class StringModelOfFile(StringModel):
    def __init__(self,
                 file: Path,
                 tmp_file_space: DirFileSpace,
                 ):
        """
        :param file: An existing regular file (that is readable).
        """
        self._file = file
        self.__tmp_file_space = tmp_file_space

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space

    @property
    def as_file(self) -> Path:
        return self._file

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._file.open() as f:
            yield f.readlines()
