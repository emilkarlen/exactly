import unittest

from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.str_.misc_formatting import lines_content, line_separated
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.logic.test_resources.string_transformer.assertions import \
    is_reference_to_string_transformer
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Arrangement, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.test_case_utils.string_matcher.num_lines.test_resources import \
    InstructionArgumentsVariantConstructor, TestCaseBase
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources.validation_cases import \
    failing_validation_cases
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _NumLinesMatches_NewLineCharacterAfterLastLine(),
        _NumLinesMatches_NoNewLineCharacterAfterLastLine(),
        _NumberOfLinesShouldBe0WhenFileIsEmpty(),

        _NumLinesDoesNotMatch(),

        _StringTransformerShouldBeValidated(),
        _WhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(),
    ])


class _NumLinesMatches_NewLineCharacterAfterLastLine(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['1',
                                         '2',
                                         '3'])
        actual_number_of_lines = '3'
        operators_that_make_comparison_true = [
            comparators.EQ.name,
            comparators.LTE.name,
        ]
        for operator in operators_that_make_comparison_true:
            with self.subTest(operator=operator):
                self._check_variants_with_expectation_type(
                    InstructionArgumentsVariantConstructor(operator=operator,
                                                           operand=actual_number_of_lines),
                    expected_result_of_positive_test=PassOrFail.PASS,
                    actual_file_contents=actual_contents,
                )


class _NumLinesMatches_NoNewLineCharacterAfterLastLine(TestCaseBase):
    def runTest(self):
        actual_contents = line_separated(['1',
                                          '2',
                                          '3',
                                          '4'])
        actual_number_of_lines = '4'
        operators_that_make_comparison_true = [
            comparators.EQ.name,
            comparators.GTE.name,
        ]
        for operator in operators_that_make_comparison_true:
            with self.subTest(operator=operator):
                self._check_variants_with_expectation_type(
                    InstructionArgumentsVariantConstructor(operator=operator,
                                                           operand=actual_number_of_lines),
                    expected_result_of_positive_test=PassOrFail.PASS,
                    actual_file_contents=actual_contents,
                )


class _NumberOfLinesShouldBe0WhenFileIsEmpty(TestCaseBase):
    def runTest(self):
        actual_contents = ''
        actual_number_of_lines = '0'
        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(operator=comparators.EQ.name,
                                                   operand=actual_number_of_lines),
            expected_result_of_positive_test=PassOrFail.PASS,
            actual_file_contents=actual_contents,
        )


class _NumLinesDoesNotMatch(TestCaseBase):
    def runTest(self):
        actual_contents = line_separated(['1',
                                          '2'])
        greater_than_actual_number_of_lines = '3'
        operators_that_make_comparison_false = [
            comparators.EQ.name,
            comparators.GT.name,
        ]
        for operator in operators_that_make_comparison_false:
            with self.subTest(operator=operator):
                self._check_variants_with_expectation_type(
                    InstructionArgumentsVariantConstructor(operator=operator,
                                                           operand=greater_than_actual_number_of_lines),
                    expected_result_of_positive_test=PassOrFail.FAIL,
                    actual_file_contents=actual_contents,
                )


class _StringTransformerShouldBeValidated(TestCaseBase):
    def runTest(self):
        for case in failing_validation_cases():
            for expectation_type in ExpectationType:
                with self.subTest(validation_case=case.name,
                                  expectation_type=expectation_type):
                    self._check(
                        remaining_source(
                            InstructionArgumentsVariantConstructor(
                                transformer=case.value.symbol_context.name,
                                operator=comparators.EQ.name,
                                operand='0'
                            ).construct(expectation_type)
                        ),
                        integration_check.empty_model(),
                        Arrangement(
                            symbols=case.value.symbol_context.symbol_table
                        ),
                        Expectation(
                            ParseExpectation(
                                symbol_references=case.value.symbol_context.references_assertion,
                            ),
                            ExecutionExpectation(
                                validation=case.value.expectation,
                            ),
                        ),
                    )


class _WhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = StringTransformerSymbolContext.of_primitive(
            'the_transformer',
            string_transformers.keep_single_line(1)
        )

        actual_original_contents = lines_content(['1',
                                                  '2',
                                                  '3'])

        number_of_lines_after_transformation = '1'

        symbol_table_with_transformer = SymbolTable({
            named_transformer.name: named_transformer.symbol_table_container
        })

        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_transformer(named_transformer.name)
        ])

        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(
                operator=comparators.EQ.name,
                operand=number_of_lines_after_transformation,
                transformer=named_transformer.name),
            expected_result_of_positive_test=PassOrFail.PASS,
            actual_file_contents=actual_original_contents,
            symbols=symbol_table_with_transformer,
            expected_symbol_references=expected_symbol_references,
        )
