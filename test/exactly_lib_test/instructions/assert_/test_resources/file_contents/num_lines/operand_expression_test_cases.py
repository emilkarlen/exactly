import unittest

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.num_lines.utils import \
    TestCaseBase
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.symbol.test_resources.string import is_reference_to_string_made_up_of_just_strings__usage, \
    StringSymbolContext
from exactly_lib_test.test_case.result.test_resources import svh_assertions as asrt_svh
from exactly_lib_test.test_case_utils.string_matcher.num_lines.test_resources import \
    InstructionArgumentsVariantConstructor
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_case_constructors = [

        _NumLinesMatchesWithOperandAsSymbolReference,
        _NumLinesMatchesWithOperandAsPythonExpression,
        _NumLinesMatchesWithOperandAsSymbolReferenceAsPartOfPythonExpression,

        _ValidationPreSdsShouldFailWhenOperandIsNotExpressionThatEvaluatesToAnInteger,
    ]

    return unittest.TestSuite([
        test_case_constructor(configuration)
        for test_case_constructor in test_case_constructors
    ])


class _NumLinesMatchesWithOperandAsSymbolReference(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['1',
                                         '2',
                                         '3',
                                         '4'])
        actual_number_of_lines = '4'
        operand_symbol = StringSymbolContext.of_constant('operand_symbol',
                                                         actual_number_of_lines)

        symbol_table_with_operand_symbol = operand_symbol.symbol_table

        expected_symbol_usages = asrt.matches_sequence([
            is_reference_to_string_made_up_of_just_strings__usage(operand_symbol.name)
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
        operand_symbol = StringSymbolContext.of_constant('operand_symbol',
                                                         symbol_value)

        expression_that_evaluates_to_actual_number_of_lines = '{sym_ref}+{const}'.format(
            sym_ref=symbol_reference_syntax_for_name(operand_symbol.name),
            const=constant_value,
        )

        symbol_table_with_operand_symbol = operand_symbol.symbol_table

        expected_symbol_usages = asrt.matches_sequence([
            is_reference_to_string_made_up_of_just_strings__usage(operand_symbol.name)
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
        cases = [
            'not_an_int',
            '1+not_an_int',
            '1.5',
            '(1',
        ]
        actual_file_contents = 'actual file contents'

        for invalid_expression in cases:
            with self.subTest(invalid_value=invalid_expression):
                args_variant_constructor = InstructionArgumentsVariantConstructor(
                    operator=comparators.NE.name,
                    operand=invalid_expression)
                self._check_single_expression_type(
                    args_variant_constructor,
                    ExpectationType.POSITIVE,
                    arrangement=
                    self.configuration.arrangement_for_contents(
                        actual_file_contents),
                    expectation=
                    Expectation(validation_pre_sds=asrt_svh.is_validation_error())
                )
