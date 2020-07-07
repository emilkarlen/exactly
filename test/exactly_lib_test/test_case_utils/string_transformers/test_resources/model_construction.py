from typing import List

from exactly_lib.test_case_utils.string_models.tmp_path_generators import PathGeneratorOfExclusiveDir
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils import TmpDirFileSpace
from exactly_lib_test.test_case_utils.string_transformers.test_resources.transformer_checker import ModelConstructor
from exactly_lib_test.test_case_utils.test_resources import string_models


def of_lines(lines: List[str]) -> ModelConstructor:
    def ret_val(tmp_file_space: TmpDirFileSpace) -> StringModel:
        return string_models.StringModelFromLines(
            lines,
            PathGeneratorOfExclusiveDir(tmp_file_space.new_path())
        )

    return ret_val


def arbitrary_model_constructor() -> ModelConstructor:
    return of_lines(['string transformer model line'])
