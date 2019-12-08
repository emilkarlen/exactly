import unittest
from typing import Callable

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Arrangement, Expectation
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments

ModelConstructor = Callable[[Tcds], LineMatcherLine]

ARBITRARY_MODEL = integration_check.constant_model((1, 'arbitrary model line'))


def constant_model(model: LineMatcherLine) -> ModelConstructor:
    return integration_check.constant_model(model)


def check(put: unittest.TestCase,
          source: ParseSource,
          model_constructor: ModelConstructor,
          arrangement: Arrangement,
          expectation: Expectation):
    integration_check.check(put,
                            source,
                            model_constructor,
                            parse_line_matcher.parser(),
                            arrangement,
                            LogicValueType.LINE_MATCHER,
                            ValueType.LINE_MATCHER,
                            expectation)


def check_with_source_variants(put: unittest.TestCase,
                               arguments: Arguments,
                               model_constructor: ModelConstructor,
                               arrangement: Arrangement,
                               expectation: Expectation):
    integration_check.check_with_source_variants(put,
                                                 arguments,
                                                 model_constructor,
                                                 parse_line_matcher.parser(),
                                                 arrangement,
                                                 LogicValueType.LINE_MATCHER,
                                                 ValueType.LINE_MATCHER,
                                                 expectation)
