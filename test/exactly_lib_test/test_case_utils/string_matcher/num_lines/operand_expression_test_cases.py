import unittest

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.condition.integer.test_resources.integer_sdv import \
    is_reference_to_symbol_in_expression
from exactly_lib_test.test_case_utils.condition.integer.test_resources.validation_cases import \
    failing_integer_validation_cases
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Arrangement, Expectation, \
    ParseExpectation, ExecutionExpectation
from exactly_lib_test.test_case_utils.string_matcher.num_lines.test_resources import \
    InstructionArgumentsVariantConstructor, TestCaseBase
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _NumLinesMatchesWithOperandAsSymbolReference(),
        _NumLinesMatchesWithOperandAsPythonExpression(),
        _NumLinesMatchesWithOperandAsSymbolReferenceAsPartOfPythonExpression(),

        _ValidationPreSdsShouldFailWhenOperandIsNotExpressionThatEvaluatesToAnInteger(),
    ])


class _NumLinesMatchesWithOperandAsSymbolReference(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['1',
                                         '2',
                                         '3',
                                         '4'])
        actual_number_of_lines = '4'
        operand_symbol = NameAndValue('operand_symbol',
                                      string_sdvs.str_constant(
                                          actual_number_of_lines))

        symbol_table_with_operand_symbol = SymbolTable({
            operand_symbol.name: container(operand_symbol.value)
        })

        expected_symbol_usages = asrt.matches_sequence([
            is_reference_to_symbol_in_expression(operand_symbol.name)
        ])

        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(
                operator=comparators.GTE.name,
                operand=symbol_reference_syntax_for_name(operand_symbol.name)),
            expected_result_of_positive_test=PassOrFail.PASS,
            actual_file_contents=actual_contents,
            symbols=symbol_table_with_operand_symbol,
            expected_symbol_usages=expected_symbol_usages,
        )


class _NumLinesMatchesWithOperandAsSymbolReferenceAsPartOfPythonExpression(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['1',
                                         '2',
                                         '3',
                                         '4'])
        symbol_value = '3'
        constant_value = '1'
        operand_symbol = NameAndValue('operand_symbol',
                                      string_sdvs.str_constant(symbol_value))

        expression_that_evaluates_to_actual_number_of_lines = '{sym_ref}+{const}'.format(
            sym_ref=symbol_reference_syntax_for_name(operand_symbol.name),
            const=constant_value,
        )

        symbol_table_with_operand_symbol = SymbolTable({
            operand_symbol.name: container(operand_symbol.value)
        })

        expected_symbol_usages = asrt.matches_sequence([
            is_reference_to_symbol_in_expression(operand_symbol.name)
        ])

        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(
                operator=comparators.GTE.name,
                operand=expression_that_evaluates_to_actual_number_of_lines),
            expected_result_of_positive_test=PassOrFail.PASS,
            actual_file_contents=actual_contents,
            symbols=symbol_table_with_operand_symbol,
            expected_symbol_usages=expected_symbol_usages,
        )


class _NumLinesMatchesWithOperandAsPythonExpression(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['1',
                                         '2',
                                         '3',
                                         '4'])
        actual_number_of_lines_expression = '2*2'

        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(operator=comparators.EQ.name,
                                                   operand=actual_number_of_lines_expression),
            expected_result_of_positive_test=PassOrFail.PASS,
            actual_file_contents=actual_contents,
        )


class _ValidationPreSdsShouldFailWhenOperandIsNotExpressionThatEvaluatesToAnInteger(TestCaseBase):
    def runTest(self):
        for case in failing_integer_validation_cases():
            with self.subTest(invalid_value=case.case_name):
                args_variant_constructor = InstructionArgumentsVariantConstructor(
                    operator=comparators.NE.name,
                    operand=case.integer_expr_string)
                self._check_single_expression_type(
                    args_variant_constructor,
                    ExpectationType.POSITIVE,
                    integration_check.ARBITRARY_MODEL,
                    arrangement=
                    Arrangement(
                        symbols=case.symbol_table
                    ),
                    expectation=
                    Expectation(
                        ParseExpectation(
                            symbol_references=case.symbol_references_expectation,
                        ),
                        ExecutionExpectation(
                            validation=case.expectation,
                        ),
                    )
                )