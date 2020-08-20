import pathlib
from typing import Callable

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelOptionType
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib_test.test_case_utils.file_matcher.test_resources import file_matcher_models
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.matcher_checker import \
    MatcherPropertiesConfiguration

ModelConstructor = Callable[[FullResolvingEnvironment], FileMatcherModel]


def constant_path(path: DescribedPath) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        return file_matcher_models.new_model__of_described(path)

    return ret_val


def constant_relative_file_name(file_name: str) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        return file_matcher_models.new_model(pathlib.Path(file_name))

    return ret_val


def file_in_sds(relativity: RelSdsOptionType, file_name: str) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        ddv = paths.rel_sandbox(relativity, paths.constant_path_part(file_name))
        return file_matcher_models.new_model__of_described(ddv.value_of_any_dependency__d(environment.tcds))

    return ret_val


def file_in_tcds(relativity: RelOptionType, file_name: str) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        ddv = paths.of_rel_option(relativity, paths.constant_path_part(file_name))
        return file_matcher_models.new_model__of_described(ddv.value_of_any_dependency__d(environment.tcds))

    return ret_val


ARBITRARY_MODEL = constant_relative_file_name('arbitrary-file.txt')

CHECKER = integration_check.IntegrationChecker(
    parse_file_matcher.parsers().full,
    MatcherPropertiesConfiguration(),
    False,
)
