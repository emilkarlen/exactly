import pathlib
from typing import Callable

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.file_matcher.test_resources import file_matcher_models
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check

ModelConstructor = Callable[[FullResolvingEnvironment], FileMatcherModel]


def constant_path(path: DescribedPath) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        return file_matcher_models.new_model__of_described(path)

    return ret_val


def constant_relative_file_name(file_name: str) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        return file_matcher_models.new_model(pathlib.Path(file_name))

    return ret_val


ARBITRARY_MODEL = constant_relative_file_name('arbitrary-file.txt')

CHECKER = integration_check.MatcherChecker(
    parse_file_matcher.parser(),
    LogicValueType.FILE_MATCHER
)
