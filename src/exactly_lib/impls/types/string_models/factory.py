from abc import ABC
from pathlib import Path

from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from . import constant_str
from . import file_model


class RootStringModelFactory(ABC):
    def __init__(self, tmp_file_space: DirFileSpace):
        self._tmp_file_space = tmp_file_space

    def of_file(self, file: Path) -> StringModel:
        return file_model.StringModelOfFile(
            file,
            self._tmp_file_space,
        )

    def of_const_str(self, contents: str) -> StringModel:
        return constant_str.StringModel(
            contents,
            self._tmp_file_space,
        )
