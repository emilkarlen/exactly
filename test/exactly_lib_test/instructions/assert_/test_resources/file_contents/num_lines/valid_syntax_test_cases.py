import itertools
import unittest

from exactly_lib.instructions.assert_.utils.expression import comparators
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.util.string import lines_content, line_separated
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.num_lines.utils import \
    InstructionArgumentsVariantConstructor, TestCaseBase
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.symbol.test_resources.lines_transformer import is_lines_transformer_reference_to
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_case_constructors = [
        _NumLinesMatches_NewLineCharacterAfterLastLine,
        _NumLinesMatches_NoNewLineCharacterAfterLastLine,
        _NumberOfLinesShouldBe0WhenFileIsEmpty,

        _NumLinesDoesNotMatch,

        _WhenLinesTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents,
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


class _WhenLinesTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = NameAndValue('the_transformer',
                                         LinesTransformerConstant(
                                             _DeleteAllButFirstLine()))

        actual_original_contents = lines_content(['1',
                                                  '2',
                                                  '3'])

        number_of_lines_after_transformation = '1'

        symbol_table_with_transformer = SymbolTable({
            named_transformer.name: container(named_transformer.value)
        })

        expected_symbol_usages = asrt.matches_sequence([
            is_lines_transformer_reference_to(named_transformer.name)
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


class _DeleteAllButFirstLine(LinesTransformer):
    def transform(self,
                  tcds: HomeAndSds,
                  lines: iter) -> iter:
        return itertools.islice(lines, 1)
