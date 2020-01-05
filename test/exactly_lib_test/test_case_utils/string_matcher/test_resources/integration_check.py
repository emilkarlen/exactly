import unittest
from typing import Callable

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand, TmpDirFileSpace
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Expectation, \
    Arrangement
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.type_system.data.test_resources import described_path

ModelConstructor = Callable[[FullResolvingEnvironment], FileToCheck]


def empty_model() -> ModelConstructor:
    return model_of('')


def model_of(contents: str) -> ModelConstructor:
    return _ModelConstructorHelper(contents).construct


class _ModelConstructorHelper:
    def __init__(self,
                 contents: str,
                 ):
        self.contents = contents

    def construct(self, environment: FullResolvingEnvironment) -> FileToCheck:
        tmp_dir_file_space = TmpDirFileSpaceAsDirCreatedOnDemand(environment.tcds.sds.internal_tmp_dir)
        original_file_path = self._create_original_file(tmp_dir_file_space)

        return FileToCheck(
            original_file_path,
            IdentityStringTransformer(),
            DestinationFilePathGetter(),
        )

    def _create_original_file(self, file_space: TmpDirFileSpace) -> DescribedPath:
        original_file_path = file_space.new_path()

        with original_file_path.open(mode='w') as f:
            f.write(self.contents)

        return described_path.new_primitive(original_file_path)


ARBITRARY_MODEL = empty_model()


def constant_model(model: FileToCheck) -> ModelConstructor:
    return integration_check.constant_model(model)


def check(put: unittest.TestCase,
          source: ParseSource,
          model: ModelConstructor,
          arrangement: Arrangement,
          expectation: Expectation):
    integration_check.check(put, source, model, parse_string_matcher.string_matcher_parser(), arrangement,
                            LogicValueType.STRING_MATCHER, ValueType.STRING_MATCHER, expectation)


def check_with_source_variants(put: unittest.TestCase,
                               arguments: Arguments,
                               model: ModelConstructor,
                               arrangement: Arrangement,
                               expectation: Expectation):
    integration_check.check_with_source_variants(put, arguments, model, parse_string_matcher.string_matcher_parser(),
                                                 arrangement, LogicValueType.STRING_MATCHER, ValueType.STRING_MATCHER,
                                                 expectation)
