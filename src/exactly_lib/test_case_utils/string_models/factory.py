from abc import ABC
from pathlib import Path

from exactly_lib.type_system.logic.string_model import StringModel
from . import file_model
from ...util.file_utils.dir_file_space import DirFileSpace


class StringModelFactory(ABC):
    def __init__(self, tmp_file_space: DirFileSpace):
        self._tmp_file_space = tmp_file_space

    def of_file(self, file: Path) -> StringModel:
        return file_model.StringModelOfFile(
            file,
            self._tmp_file_space.sub_dir_space(),
        )
