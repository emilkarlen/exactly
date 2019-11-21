"""
Test of test-infrastructure: instruction_check.
"""
import unittest
from typing import List, Sequence

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_value_validation import ConstantPreOrPostSdsValueValidator
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTraceAndNegation, MatcherDdv
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.section_document.test_resources.parser_classes import ConstantParser
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as asrt_sym
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers, integration_check as sut
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Expectation
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import is_hard_error
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.render.test_resources import renderers

EXPECTED_LOGIC_TYPE_FOR_TEST = LogicValueType.LINE_MATCHER
UNEXPECTED_LOGIC_TYPE_FOR_TEST = LogicValueType.FILE_MATCHER

EXPECTED_VALUE_TYPE_FOR_TEST = ValueType.LINE_MATCHER
UNEXPECTED_VALUE_TYPE_FOR_TEST = ValueType.FILE_MATCHER


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestDefault))
    ret_val.addTest(unittest.makeSuite(TestTypes))
    ret_val.addTest(unittest.makeSuite(TestFailingExpectations))
    ret_val.addTest(unittest.makeSuite(TestSymbolReferences))
    ret_val.addTest(unittest.makeSuite(TestHardError))
    return ret_val


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.tc = utils.TestCaseWithTestErrorAsFailureException()

    def _check_line_matcher_type(self,
                                 source: ParseSource,
                                 model: int,
                                 parser: Parser[MatcherTypeSdv[int]],
                                 arrangement: sut.Arrangement,
                                 expectation: sut.Expectation):
        sut.check(self.tc, source, model, parser, arrangement,
                  EXPECTED_LOGIC_TYPE_FOR_TEST,
                  EXPECTED_VALUE_TYPE_FOR_TEST,
                  expectation)


class TestSymbolReferences(TestCaseBase):
    def test_that_fails_due_to_missing_symbol_reference(self):
        with self.assertRaises(utils.TestError):
            symbol_usages_of_matcher = []
            symbol_usages_of_expectation = [data_symbol_utils.symbol_reference('symbol_name')]
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                _constant_line_matcher_type_parser_of_matcher_sdv(
                    matchers.sdv_from_primitive_value(references=symbol_usages_of_matcher)
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

        sdv_that_checks_symbols = _MatcherSdvThatAssertsThatSymbolsAreAsExpected(self, expectation)

        self._check_line_matcher_type(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            _constant_line_matcher_type_parser_of_matcher_sdv(sdv_that_checks_symbols),
            sut.Arrangement(
                symbols=symbol_table_of_arrangement),
            sut.Expectation(),
        )


class TestHardError(TestCaseBase):
    def test_missing_hard_error_is_detected(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
                sut.Arrangement(),
                sut.Expectation(
                    is_hard_error=is_hard_error(),
                ))


class TestTypes(TestCaseBase):
    def test_expect_given_logic_value_type(self):
        with self.assertRaises(utils.TestError):
            sut.check(
                self.tc,
                utils.single_line_source(),
                ARBITRARY_MODEL,
                PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
                sut.Arrangement(),
                UNEXPECTED_LOGIC_TYPE_FOR_TEST,
                EXPECTED_VALUE_TYPE_FOR_TEST,
                sut.Expectation(),
            )

    def test_expect_given_value_type(self):
        with self.assertRaises(utils.TestError):
            sut.check(
                self.tc,
                utils.single_line_source(),
                ARBITRARY_MODEL,
                PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
                sut.Arrangement(),
                EXPECTED_LOGIC_TYPE_FOR_TEST,
                UNEXPECTED_VALUE_TYPE_FOR_TEST,
                sut.Expectation(),
            )


class TestDefault(TestCaseBase):

    def test_expect_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [data_symbol_utils.symbol_reference('symbol_name')]
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                _constant_line_matcher_type_parser_of_matcher_sdv(
                    matchers.sdv_from_primitive_value(references=unexpected_symbol_usages)
                ),
                sut.Arrangement(),
                sut.Expectation(),
            )

    def test_expect_pre_validation_succeeds(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(utils.single_line_source(),
                                          ARBITRARY_MODEL,
                                          _constant_line_matcher_type_parser_of_matcher_ddv(
                                              matchers.MatcherDdvOfConstantMatcherTestImpl(
                                                  matchers.MatcherWithConstantResult(True),
                                                  ConstantPreOrPostSdsValueValidator(
                                                      pre_sds_result=rend_comb.ConstantSequenceR([])
                                                  )
                                              )
                                          ),
                                          sut.Arrangement(),
                                          Expectation(),
                                          )

    def test_expect_post_validation_succeeds(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(utils.single_line_source(),
                                          ARBITRARY_MODEL,
                                          _constant_line_matcher_type_parser_of_matcher_ddv(
                                              matchers.MatcherDdvOfConstantMatcherTestImpl(
                                                  matchers.MatcherWithConstantResult(True),
                                                  ConstantPreOrPostSdsValueValidator(
                                                      post_sds_result=rend_comb.ConstantSequenceR([])
                                                  )
                                              )
                                          ),
                                          sut.Arrangement(),
                                          Expectation(),
                                          )

    def test_expects_no_hard_error(self):
        parser_that_gives_value_that_causes_hard_error = _constant_line_matcher_type_parser_of_matcher_sdv(
            matchers.sdv_from_primitive_value(_MatcherThatReportsHardError())
        )
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                parser_that_gives_value_that_causes_hard_error,
                sut.Arrangement(),
                sut.Expectation(),
            )

    def test_expect_match_is_true(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                _constant_line_matcher_type_parser_of_matcher_sdv(
                    matchers.sdv_from_primitive_value(
                        matchers.MatcherWithConstantResult(False)
                    )
                ),
                sut.Arrangement(),
                sut.Expectation())

    def test_successful_flow(self):
        self._check_line_matcher_type(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
            sut.Arrangement(),
            sut.Expectation())


class TestFailingExpectations(TestCaseBase):
    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(utils.single_line_source(),
                                          ARBITRARY_MODEL,
                                          ConstantParser(_MATCHER_THAT_MATCHES),
                                          sut.Arrangement(),
                                          Expectation(
                                              validation=asrt_validation.pre_sds_validation_fails(),
                                          )
                                          )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(utils.single_line_source(),
                                          ARBITRARY_MODEL,
                                          ConstantParser(_MATCHER_THAT_MATCHES),
                                          sut.Arrangement(),
                                          Expectation(
                                              validation=asrt_validation.post_sds_validation_fails(),
                                          )
                                          )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                ConstantParser(_MATCHER_THAT_MATCHES),
                sut.Arrangement(),
                Expectation(
                    main_result=matcher_assertions.is_arbitrary_matching_failure()),
            )


class _MatcherTypeSdvTestImpl(MatcherTypeSdv[int]):
    def __init__(self,
                 matcher: MatcherSdv[int],
                 ):
        self._matcher = matcher

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.LINE_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.LINE_MATCHER

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._matcher.references

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[int]:
        return self._matcher.resolve(symbols)


class _MatcherThatReportsHardError(MatcherWTraceAndNegation[int]):
    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return 'unconditional HARD ERROR'

    def _structure(self) -> StructureRenderer:
        return renderers.structure_renderer_for_arbitrary_object(self)

    @property
    def negation(self) -> MatcherWTraceAndNegation[int]:
        return self

    def matches_w_trace(self, model: int) -> MatchingResult:
        raise HardErrorException(new_single_string_text_for_test('unconditional hard error'))

    def matches(self, model: int) -> bool:
        raise HardErrorException(new_single_string_text_for_test('unconditional hard error'))


class _MatcherSdvThatAssertsThatSymbolsAreAsExpected(MatcherSdv[int]):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: ValueAssertion[SymbolTable]):
        self._put = put
        self._expectation = expectation

    @property
    def references(self) -> List[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[int]:
        self._expectation.apply_with_message(self._put, symbols, 'symbols given to resolve')

        return matchers.ddv_of_unconditionally_matching_matcher()


def _line_matcher_type_sdv(matcher: MatcherSdv[int]) -> MatcherTypeSdv[int]:
    return _MatcherTypeSdvTestImpl(matcher)


def _constant_line_matcher_type_parser_of_matcher_sdv(matcher: MatcherSdv[int]) -> Parser[_MatcherTypeSdvTestImpl]:
    return ConstantParser(_line_matcher_type_sdv(matcher))


def _constant_line_matcher_type_parser_of_matcher_ddv(matcher: MatcherDdv[int]) -> Parser[_MatcherTypeSdvTestImpl]:
    return ConstantParser(_line_matcher_type_sdv(matchers.MatcherSdvOfConstantDdvTestImpl(matcher)))


ARBITRARY_MODEL = 0

PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION = \
    _constant_line_matcher_type_parser_of_matcher_sdv(
        matchers.sdv_from_primitive_value()
    )

_MATCHER_THAT_MATCHES = _line_matcher_type_sdv(matchers.sdv_from_primitive_value())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
