from typing import List

from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.tmp_file_space import DirFileSpace
from exactly_lib_test.test_case_utils.string_transformers.test_resources.transformer_checker import ModelConstructor
from exactly_lib_test.type_system.logic.test_resources import string_models


def of_lines(lines: List[str]) -> ModelConstructor:
    def ret_val(tmp_file_space: DirFileSpace) -> StringModel:
        return string_models.StringModelFromLines(
            lines,
            tmp_file_space.sub_dir_space()
        )

    return ret_val


def arbitrary_model_constructor() -> ModelConstructor:
    return of_lines(['string transformer model line'])


def constant(result: StringModel) -> ModelConstructor:
    def ret_val(tmp_file_space: DirFileSpace) -> StringModel:
        return result

    return ret_val
