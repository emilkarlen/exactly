from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator

from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.string_model import StringModel, TmpFilePathGenerator


class StringModelOfFile(StringModel):
    def __init__(self,
                 file: DescribedPath,
                 tmp_path_generator: TmpFilePathGenerator,
                 ):
        self._file = file
        self._tmp_path_generator = tmp_path_generator

    @property
    def _path_generator(self) -> TmpFilePathGenerator:
        return self._tmp_path_generator

    @property
    def as_file(self) -> Path:
        return self._file.primitive

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._file.primitive.open() as f:
            yield f.readlines()
