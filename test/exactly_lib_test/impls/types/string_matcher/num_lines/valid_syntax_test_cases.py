import unittest

from exactly_lib.impls.types.condition import comparators
from exactly_lib.util.str_.misc_formatting import lines_content, line_separated
from exactly_lib_test.impls.types.string_matcher.num_lines.test_resources import \
    InstructionArgumentsVariantConstructor, TestCaseBase
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    PassOrFail


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _NumLinesMatches_NewLineCharacterAfterLastLine(),
        _NumLinesMatches_NoNewLineCharacterAfterLastLine(),
        _NumberOfLinesShouldBe0WhenFileIsEmpty(),

        _NumLinesDoesNotMatch(),
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
