from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator

from exactly_lib.type_system.logic.string_model import StringModel, TmpFilePathGenerator


class StringModelOfFile(StringModel):
    def __init__(self,
                 file: Path,
                 tmp_path_generator: TmpFilePathGenerator,
                 ):
        """
        :param file: An existing regular file (that is readable).
        """
        self._file = file
        self._tmp_path_generator = tmp_path_generator

    @property
    def _path_generator(self) -> TmpFilePathGenerator:
        return self._tmp_path_generator

    @property
    def as_file(self) -> Path:
        return self._file

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._file.open() as f:
            yield f.readlines()
