from abc import ABC
from pathlib import Path

from exactly_lib.type_system.logic.string_model import StringModel


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
