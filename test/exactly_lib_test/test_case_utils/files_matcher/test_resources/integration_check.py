import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import ModelConstructor
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Arrangement, Expectation
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments


def check(put: unittest.TestCase,
          source: ParseSource,
          model_constructor: ModelConstructor,
          arrangement: Arrangement,
          expectation: Expectation):
    integration_check.check(put,
                            source,
                            model_constructor,
                            parse_files_matcher.files_matcher_parser(),
                            arrangement,
                            LogicValueType.FILES_MATCHER,
                            ValueType.FILES_MATCHER,
                            expectation)


def check_with_source_variants(put: unittest.TestCase,
                               arguments: Arguments,
                               model_constructor: ModelConstructor,
                               arrangement: Arrangement,
                               expectation: Expectation):
    integration_check.check_with_source_variants(put,
                                                 arguments,
                                                 model_constructor,
                                                 parse_files_matcher.files_matcher_parser(),
                                                 arrangement,
                                                 LogicValueType.FILES_MATCHER,
                                                 ValueType.FILES_MATCHER,
                                                 expectation)
