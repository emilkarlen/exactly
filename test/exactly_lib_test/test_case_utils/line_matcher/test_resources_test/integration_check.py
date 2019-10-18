"""
Test of test-infrastructure: instruction_check.
"""
import unittest
from typing import List

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine, LineMatcherValue
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.section_document.test_resources.parser_classes import ConstantParser
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as asrt_sym
from exactly_lib_test.symbol.test_resources.line_matcher import line_matcher_from_primitive_value, \
    resolver_of_unconditionally_matching_matcher, value_of_unconditionally_matching_matcher
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case_utils.line_matcher.test_resources import integration_check as sut
from exactly_lib_test.test_case_utils.line_matcher.test_resources.integration_check import Expectation, is_pass
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import is_hard_error
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.render.test_resources import renderers


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingExpectations))
    ret_val.addTest(unittest.makeSuite(TestSymbolReferences))
    ret_val.addTest(unittest.makeSuite(TestHardError))
    ret_val.addTest(unittest.makeSuite(TestMisc))
    return ret_val


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.tc = utils.TestCaseWithTestErrorAsFailureException()

    def _check(self,
               source: ParseSource,
               model: LineMatcherLine,
               parser: Parser[LineMatcherResolver],
               arrangement: sut.Arrangement,
               expectation: sut.Expectation):
        sut.check_with_custom_parser(self.tc, source, model, parser, arrangement, expectation)


class TestSymbolReferences(TestCaseBase):
    def test_that_default_expectation_assumes_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [data_symbol_utils.symbol_reference('symbol_name')]
            self._check(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                ConstantParser(
                    line_matcher_from_primitive_value(references=unexpected_symbol_usages)
                ),
                sut.Arrangement(),
                sut.Expectation(),
            )

    def test_that_fails_due_to_missing_symbol_reference(self):
        with self.assertRaises(utils.TestError):
            symbol_usages_of_matcher = []
            symbol_usages_of_expectation = [data_symbol_utils.symbol_reference('symbol_name')]
            self._check(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                ConstantParser(
                    line_matcher_from_primitive_value(references=symbol_usages_of_matcher)
                ),
                sut.Arrangement(),
                sut.Expectation(
                    symbol_references=sym_asrt.equals_symbol_references(symbol_usages_of_expectation)),
            )

    def test_that_symbols_from_arrangement_exist_in_environment(self):
        symbol_name = 'symbol_name'
        symbol_value = 'the symbol value'
        symbol_table_of_arrangement = data_symbol_utils.symbol_table_with_single_string_value(symbol_name,
                                                                                              symbol_value)
        expected_symbol_table = data_symbol_utils.symbol_table_with_single_string_value(symbol_name,
                                                                                        symbol_value)
        expectation = asrt_sym.equals_symbol_table(expected_symbol_table)

        resolver_that_checks_symbols = LineMatcherResolverThatAssertsThatSymbolsAreAsExpected(self, expectation)

        self._check(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            ConstantParser(resolver_that_checks_symbols),
            sut.Arrangement(
                symbols=symbol_table_of_arrangement),
            sut.Expectation(),
        )


class TestHardError(TestCaseBase):
    def test_expected_hard_error_is_detected(self):
        parser_that_gives_value_that_causes_hard_error = ConstantParser(
            line_matcher_from_primitive_value(_LineMatcherThatReportsHardError())
        )
        self._check(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            parser_that_gives_value_that_causes_hard_error,
            sut.Arrangement(),
            sut.Expectation(
                is_hard_error=is_hard_error(),
            ))

    def test_missing_hard_error_is_detected(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
                sut.Arrangement(),
                sut.Expectation(
                    is_hard_error=is_hard_error(),
                ))


class TestMisc(TestCaseBase):
    def test_successful_flow(self):
        self._check(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
            sut.Arrangement(),
            is_pass())


class TestFailingExpectations(TestCaseBase):
    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.single_line_source(),
                        ARBITRARY_MODEL,
                        ConstantParser(_MATCHER_THAT_MATCHES),
                        sut.Arrangement(),
                        Expectation(
                            validation=asrt_validation.pre_sds_validation_fails(),
                        )
                        )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.single_line_source(),
                        ARBITRARY_MODEL,
                        ConstantParser(_MATCHER_THAT_MATCHES),
                        sut.Arrangement(),
                        Expectation(
                            validation=asrt_validation.post_sds_validation_fails(),
                        )
                        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                ConstantParser(_MATCHER_THAT_MATCHES),
                sut.Arrangement(),
                Expectation(
                    main_result=matcher_assertions.is_arbitrary_matching_failure()),
            )


class _LineMatcherThatReportsHardError(LineMatcher):
    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return 'unconditional HARD ERROR'

    def _structure(self) -> StructureRenderer:
        return renderers.structure_renderer_for_arbitrary_object(self)

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        raise HardErrorException(new_single_string_text_for_test('unconditional hard error'))

    def matches(self, model: LineMatcherLine) -> bool:
        raise HardErrorException(new_single_string_text_for_test('unconditional hard error'))


class LineMatcherResolverThatAssertsThatSymbolsAreAsExpected(LineMatcherResolver):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: ValueAssertion[SymbolTable]):
        self._put = put
        self._expectation = expectation

    @property
    def references(self) -> List[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        self._expectation.apply_with_message(self._put, symbols, 'symbols given to resolve')

        return value_of_unconditionally_matching_matcher()


ARBITRARY_MODEL = (1, 'line of arbitrary model')

PARSER_THAT_GIVES_MATCHER_THAT_MATCHES = ConstantParser(line_matcher_from_primitive_value())

_MATCHER_THAT_MATCHES = resolver_of_unconditionally_matching_matcher()

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
