import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher as sut
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_case_utils.line_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Arrangement, Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success, ExpectationTypeConfigForNoneIsSuccess


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               model: LineMatcherLine,
               arrangement: Arrangement,
               expectation: Expectation):
        integration_check.check(self, source, model, arrangement, expectation)

    def _assert_failing_parse(self, source: ParseSource):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parser().parse(source)


class TestWithNegationArgumentBase(TestCaseBase):
    def runTest(self):
        for expectation_type in ExpectationType:
            with self.subTest(expectation_type=expectation_type):
                self._doTest(expectation_type_config__non_is_success(expectation_type))

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        raise NotImplementedError('abstract method')
