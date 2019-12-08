import pathlib
import unittest
from typing import Callable

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForPrimitivePath
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Arrangement, Expectation
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.type_system.data.test_resources import described_path

ModelConstructor = Callable[[Tcds], FileMatcherModel]


def constant_path(path: DescribedPathPrimitive) -> ModelConstructor:
    def ret_val(tcds: Tcds) -> FileMatcherModel:
        return _new_model(tcds, path)

    return ret_val


def constant_relative_file_name(file_name: str) -> ModelConstructor:
    def ret_val(tcds: Tcds) -> FileMatcherModel:
        return _new_model(tcds, described_path.new_primitive(pathlib.Path(file_name)))

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


def _new_model(tcds: Tcds, path: DescribedPathPrimitive) -> FileMatcherModel:
    return FileMatcherModelForPrimitivePath(
        TmpDirFileSpaceAsDirCreatedOnDemand(tcds.sds.internal_tmp_dir),
        path
    )
