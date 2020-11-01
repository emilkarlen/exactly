import unittest

from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.util.str_.misc_formatting import lines_content, line_separated
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.num_lines.utils import \
    TestCaseBase
from exactly_lib_test.test_case_utils.string_matcher.num_lines.test_resources import \
    InstructionArgumentsVariantConstructor
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.assertions import \
    is_reference_to_string_transformer__usage
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_case_constructors = [
        _NumLinesMatches_NewLineCharacterAfterLastLine,
        _NumLinesMatches_NoNewLineCharacterAfterLastLine,
        _NumberOfLinesShouldBe0WhenFileIsEmpty,

        _NumLinesDoesNotMatch,

        _WhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents,
    ]
    return unittest.TestSuite([
        test_case_constructor(configuration)
        for test_case_constructor in test_case_constructors
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


class _WhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = StringTransformerSymbolContext.of_primitive('the_transformer',
                                                                        string_transformers.keep_single_line(1))

        actual_original_contents = lines_content(['1',
                                                  '2',
                                                  '3'])

        number_of_lines_after_transformation = '1'

        symbol_table_with_transformer = named_transformer.symbol_table

        expected_symbol_usages = asrt.matches_sequence([
            is_reference_to_string_transformer__usage(named_transformer.name)
        ])

        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(
                operator=comparators.EQ.name,
                operand=number_of_lines_after_transformation,
                transformer=named_transformer.name),
            expected_result_of_positive_test=PassOrFail.PASS,
            actual_file_contents=actual_original_contents,
            symbols=symbol_table_with_transformer,
            expected_symbol_usages=expected_symbol_usages,
        )
