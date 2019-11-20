import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Arrangement, Expectation
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments


def check(put: unittest.TestCase,
          source: ParseSource,
          model: LineMatcherLine,
          arrangement: Arrangement,
          expectation: Expectation):
    integration_check.check(put,
                            source,
                            model,
                            parse_line_matcher.parser(),
                            arrangement,
                            expectation)


def check_with_source_variants(put: unittest.TestCase,
                               arguments: Arguments,
                               model: LineMatcherLine,
                               arrangement: Arrangement,
                               expectation: Expectation):
    integration_check.check_with_source_variants(put,
                                                 arguments,
                                                 model,
                                                 parse_line_matcher.parser(),
                                                 arrangement,
                                                 expectation)
