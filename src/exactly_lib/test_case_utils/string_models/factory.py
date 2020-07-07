from abc import ABC
from pathlib import Path

from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils import TmpDirFileSpace
from . import file_model, tmp_path_generators


class StringModelFactory(ABC):
    def __init__(self, tmp_file_space: TmpDirFileSpace):
        self._tmp_file_space = tmp_file_space

    def of_file(self, file: Path) -> StringModel:
        return file_model.StringModelOfFile(
            file,
            tmp_path_generators.PathGeneratorOfExclusiveDir(
                self._tmp_file_space.new_path()
            ),
        )
