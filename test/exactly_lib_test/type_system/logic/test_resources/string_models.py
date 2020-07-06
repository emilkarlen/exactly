from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import Sequence, ContextManager, Iterator

from exactly_lib.type_system.logic.string_model import StringModel, TmpFilePathGenerator


class StringModelFromLinesBase(StringModel, ABC):
    def __init__(self):
        self._as_file_path = None

    @property
    def as_file(self) -> Path:
        if self._as_file_path is None:
            self._as_file_path = self._to_file()
        return self._as_file_path

    def _to_file(self) -> Path:
        path = self._path_generator.new_path()

        with path.open('x') as f:
            with self.as_lines as lines:
                f.writelines(lines)

        return path


class ConstantRootStringModelFromLines(StringModelFromLinesBase):
    def __init__(self,
                 value: Sequence[str],
                 tmp_file_path_generator: TmpFilePathGenerator,
                 ):
        super().__init__()
        self._value = value
        self._tmp_file_path_generator = tmp_file_path_generator

    @property
    def _path_generator(self) -> TmpFilePathGenerator:
        return self._tmp_file_path_generator

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self._value)
