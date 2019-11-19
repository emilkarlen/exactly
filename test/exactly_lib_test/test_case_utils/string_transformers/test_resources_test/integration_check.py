"""
Test of test-infrastructure: instruction_check.
"""
import unittest
from typing import List

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.string_transformer import StringTransformerModel, StringTransformerDdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.section_document.test_resources.parser_classes import ConstantParser
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as asrt_sym
from exactly_lib_test.symbol.test_resources.string_transformer import string_transformer_from_primitive_value, \
    string_transformer_from_result, arbitrary_transformer_ddv, StringTransformerIdentityTestImpl
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check as sut
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import Expectation
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import is_hard_error
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.type_system.logic.string_transformer.test_resources import StringTransformerTestImplBase


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
               model: StringTransformerModel,
               parser: Parser[StringTransformerSdv],
               arrangement: sut.Arrangement,
               expectation: sut.Expectation):
        sut.check_with_custom_parser(self.tc, source, model, parser, arrangement, expectation)


class TestSymbolReferences(TestCaseBase):
    def test_that_default_expectation_assumes_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [data_symbol_utils.symbol_reference('symbol_name')]
            self._check(
                utils.single_line_source(),
                arbitrary_model(),
                ConstantParser(
                    string_transformer_from_primitive_value(references=unexpected_symbol_usages)
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
                arbitrary_model(),
                ConstantParser(
                    string_transformer_from_primitive_value(references=symbol_usages_of_matcher)
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

        sdv_that_checks_symbols = StringTransformerSdvThatAssertsThatSymbolsAreAsExpected(self, expectation)

        self._check(
            utils.single_line_source(),
            arbitrary_model(),
            ConstantParser(sdv_that_checks_symbols),
            sut.Arrangement(
                symbols=symbol_table_of_arrangement),
            sut.Expectation(is_identity_transformer=asrt.anything_goes()),
        )


class TestHardError(TestCaseBase):
    def test_expected_hard_error_is_detected(self):
        parser_that_gives_value_that_causes_hard_error = ConstantParser(
            string_transformer_from_primitive_value(_StringTransformerThatReportsHardError())
        )
        self._check(
            utils.single_line_source(),
            arbitrary_model(),
            parser_that_gives_value_that_causes_hard_error,
            sut.Arrangement(),
            sut.Expectation(
                is_hard_error=is_hard_error(),
            ))

    def test_missing_hard_error_is_detected(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.single_line_source(),
                arbitrary_model(),
                ConstantParser(arbitrary_transformer()),
                sut.Arrangement(),
                sut.Expectation(
                    is_hard_error=is_hard_error(),
                ))


class TestMisc(TestCaseBase):
    def test_successful_flow(self):
        self._check(
            utils.single_line_source(),
            arbitrary_model(),
            ConstantParser(arbitrary_transformer()),
            sut.Arrangement(),
            expectation=sut.Expectation(
                is_identity_transformer=asrt.anything_goes()
            ))


class TestFailingExpectations(TestCaseBase):
    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.single_line_source(),
                        arbitrary_model(),
                        ConstantParser(arbitrary_transformer()),
                        sut.Arrangement(),
                        Expectation(
                            validation=asrt_validation.pre_sds_validation_fails(),
                        )
                        )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(utils.single_line_source(),
                        arbitrary_model(),
                        ConstantParser(arbitrary_transformer()),
                        sut.Arrangement(),
                        Expectation(
                            validation=asrt_validation.post_sds_validation_fails(),
                        )
                        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.single_line_source(),
                arbitrary_model(),
                ConstantParser(string_transformer_from_result(model_with_num_lines(1))),
                sut.Arrangement(),
                Expectation(
                    main_result=assert_num_lines_in_result_equals(2)),
            )

    def test_fail_due_to_unexpected_is_identity_transformer(self):
        cases = [
            NEA('actual is identity transformer',
                expected=True,
                actual=string_transformer_from_primitive_value(
                    StringTransformerIdentityTestImpl()
                )),
            NEA('actual is NOT identity transformer',
                expected=False,
                actual=arbitrary_non_identity_transformer()),
        ]
        for case in cases:
            with self.subTest(case.name):
                with self.assertRaises(utils.TestError):
                    self._check(
                        utils.single_line_source(),
                        arbitrary_model(),
                        ConstantParser(case.actual),
                        sut.Arrangement(),
                        Expectation(
                            is_identity_transformer=asrt.equals(case.expected)),
                    )

    def test_default_expectation_of_is_identity_SHOULD_be_false(self):
        with self.assertRaises(utils.TestError):
            self._check(
                utils.single_line_source(),
                arbitrary_model(),
                ConstantParser(string_transformer_from_primitive_value(
                    StringTransformerIdentityTestImpl()
                )),
                sut.Arrangement(),
                Expectation(),
            )


class _StringTransformerThatReportsHardError(StringTransformerTestImplBase):
    @property
    def option_description(self) -> str:
        return 'unconditional HARD ERROR'

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        raise HardErrorException(new_single_string_text_for_test('unconditional hard error'))


class StringTransformerSdvThatAssertsThatSymbolsAreAsExpected(StringTransformerSdv):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: ValueAssertion[SymbolTable]):
        self._put = put
        self._expectation = expectation

    @property
    def references(self) -> List[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        self._expectation.apply_with_message(self._put, symbols, 'symbols given to resolve')

        return arbitrary_transformer_ddv()


class _AssertNumElements(ValueAssertionBase[StringTransformerModel]):
    def __init__(self, expected_num_lines: int):
        self.expected_num_lines = expected_num_lines

    def _apply(self,
               put: unittest.TestCase,
               value: StringTransformerModel,
               message_builder: MessageBuilder):
        actual = len(list(value))
        put.assertEqual(self.expected_num_lines,
                        actual,
                        'number of lines')


def assert_num_lines_in_result_equals(expected: int) -> ValueAssertion[StringTransformerModel]:
    return _AssertNumElements(expected)


def arbitrary_model() -> StringTransformerModel:
    return model_with_num_lines(0)


def model_with_num_lines(number_of_lines: int) -> StringTransformerModel:
    return iter(['line'] * number_of_lines)


def arbitrary_transformer() -> StringTransformerSdv:
    return string_transformer_from_result(model_with_num_lines(1))


def arbitrary_non_identity_transformer() -> StringTransformerSdv:
    return arbitrary_transformer()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
