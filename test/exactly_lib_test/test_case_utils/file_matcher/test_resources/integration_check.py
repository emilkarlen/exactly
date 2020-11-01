import pathlib
from typing import Callable

from exactly_lib.tcfs.path_relativity import RelSdsOptionType, RelOptionType
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_ddv import DescribedPath
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
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


def constant_relative_path(path: pathlib.Path) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        return file_matcher_models.new_model(path)

    return ret_val


def current_directory() -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        return file_matcher_models.new_model(pathlib.Path('.'))

    return ret_val


def file_in_sds(relativity: RelSdsOptionType, file_name: str) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        ddv = path_ddvs.rel_sandbox(relativity, path_ddvs.constant_path_part(file_name))
        return file_matcher_models.new_model__of_described(ddv.value_of_any_dependency__d(environment.tcds))

    return ret_val


def file_in_tcds(relativity: RelOptionType, file_name: str) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        ddv = path_ddvs.of_rel_option(relativity, path_ddvs.constant_path_part(file_name))
        return file_matcher_models.new_model__of_described(ddv.value_of_any_dependency__d(environment.tcds))

    return ret_val


ARBITRARY_MODEL = constant_relative_file_name('arbitrary-file.txt')

CHECKER__PARSE_FULL = integration_check.IntegrationChecker(
    parse_file_matcher.parsers().full,
    MatcherPropertiesConfiguration(),
    False,
)

CHECKER__PARSE_SIMPLE = integration_check.IntegrationChecker(
    parse_file_matcher.parsers().simple,
    MatcherPropertiesConfiguration(),
    False,
)
