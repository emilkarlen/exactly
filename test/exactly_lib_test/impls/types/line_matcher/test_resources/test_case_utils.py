import unittest

from exactly_lib.impls.types.line_matcher import parse_line_matcher as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.line_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.line_matcher.test_resources.models import ModelConstructor
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Expectation
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success, ExpectationTypeConfigForNoneIsSuccess


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               model_constructor: ModelConstructor,
               arrangement: SymbolTable,
               expectation: Expectation):
        integration_check.check(self, source, model_constructor,
                                arrangement,
                                expectation)

    def _assert_failing_parse(self, source: ParseSource):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parsers().full.parse(source)


class TestWithNegationArgumentBase(TestCaseBase):
    def runTest(self):
        for expectation_type in ExpectationType:
            with self.subTest(expectation_type=expectation_type):
                self._doTest(expectation_type_config__non_is_success(expectation_type))

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        raise NotImplementedError('abstract method')
