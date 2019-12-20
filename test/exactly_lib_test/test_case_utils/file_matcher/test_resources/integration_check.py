import pathlib
import unittest
from typing import Callable

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib_test.test_case_utils.file_matcher.test_resources import file_matcher_models
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Arrangement, Expectation
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments

ModelConstructor = Callable[[FullResolvingEnvironment], FileMatcherModel]


def constant_path(path: DescribedPathPrimitive) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        return file_matcher_models.new_model__of_described(path)

    return ret_val


def constant_relative_file_name(file_name: str) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FileMatcherModel:
        return file_matcher_models.new_model(pathlib.Path(file_name))

    return ret_val


ARBITRARY_MODEL = constant_relative_file_name('arbitrary-file.txt')


def check(put: unittest.TestCase,
          source: ParseSource,
          model_constructor: ModelConstructor,
          arrangement: Arrangement,
          expectation: Expectation):
    integration_check.check(put,
                            source,
                            model_constructor,
                            parse_file_matcher.parser(),
                            arrangement,
                            LogicValueType.FILE_MATCHER,
                            ValueType.FILE_MATCHER,
                            expectation)


def check_with_source_variants(put: unittest.TestCase,
                               arguments: Arguments,
                               model_constructor: ModelConstructor,
                               arrangement: Arrangement,
                               expectation: Expectation):
    integration_check.check_with_source_variants(put,
                                                 arguments,
                                                 model_constructor,
                                                 parse_file_matcher.parser(),
                                                 arrangement,
                                                 LogicValueType.FILE_MATCHER,
                                                 ValueType.FILE_MATCHER,
                                                 expectation)
