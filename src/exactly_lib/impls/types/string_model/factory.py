from abc import ABC
from pathlib import Path

from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.path_describer import PathDescriberForPrimitive
from exactly_lib.type_val_prims.string_model.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from . import constant_str
from . import file_model


class RootStringModelFactory(ABC):
    def __init__(self, tmp_file_space: DirFileSpace):
        self._tmp_file_space = tmp_file_space

    def of_file__poorly_described(self, file: Path) -> StringModel:
        return file_model.string_model_of_file__poorly_described(
            file,
            self._tmp_file_space,
        )

    def of_file__described(self, file: DescribedPath) -> StringModel:
        return file_model.string_model_of_file__described(
            file,
            self._tmp_file_space,
        )

    def of_file(self,
                path: Path,
                describer: PathDescriberForPrimitive,
                ) -> StringModel:
        return file_model.StringModelOfFile(
            path,
            describer,
            self._tmp_file_space,
        )

    def of_const_str(self, contents: str) -> StringModel:
        return constant_str.StringModel(
            contents,
            self._tmp_file_space,
        )
