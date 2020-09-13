from typing import List

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib_test.test_case_utils.string_transformers.test_resources.transformer_checker import ModelConstructor
from exactly_lib_test.type_system.logic.string_model.test_resources import string_models


def of_lines(lines: List[str]) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> StringModel:
        return string_models.StringModelFromLines(
            lines,
            environment.application_environment.tmp_files_space.sub_dir_space()
        )

    return ret_val


def arbitrary_model_constructor() -> ModelConstructor:
    return of_lines(['string transformer model line'])


def constant(result: StringModel) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> StringModel:
        return result

    return ret_val
