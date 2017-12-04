import unittest

from exactly_lib.symbol.data.string_resolver import string_constant
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.num_lines.utils import \
    InstructionArgumentsVariantConstructor, TestCaseBase
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.symbol.test_resources.string import is_string_made_up_of_just_strings_reference_to
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.test_resources import svh_assertions as asrt_svh
from exactly_lib_test.test_resources.name_and_value import NameAndValue
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
        operand_symbol = NameAndValue('operand_symbol',
                                      string_constant(actual_number_of_lines))

        symbol_table_with_operand_symbol = SymbolTable({
            operand_symbol.name: container(operand_symbol.value)
        })

        expected_symbol_usages = asrt.matches_sequence([
            is_string_made_up_of_just_strings_reference_to(operand_symbol.name)
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
                                      string_constant(symbol_value))

        expression_that_evaluates_to_actual_number_of_lines = '{sym_ref}+{const}'.format(
            sym_ref=symbol_reference_syntax_for_name(operand_symbol.name),
            const=constant_value,
        )

        symbol_table_with_operand_symbol = SymbolTable({
            operand_symbol.name: container(operand_symbol.value)
        })

        expected_symbol_usages = asrt.matches_sequence([
            is_string_made_up_of_just_strings_reference_to(operand_symbol.name)
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
                    Expectation(validation_pre_sds=asrt_svh.is_validation_error(asrt.anything_goes()))
                )
