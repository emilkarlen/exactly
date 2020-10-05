import unittest

from exactly_lib.definitions import logic
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.integer_matcher import IntegerMatcherSymbolContext, \
    IntegerMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.symbol.test_resources.string import StringSymbolContext
from exactly_lib_test.test_case_utils.integer.test_resources.integer_sdv import \
    is_reference_to_symbol_in_expression
from exactly_lib_test.test_case_utils.integer.test_resources.validation_cases import \
    failing_integer_validation_cases
from exactly_lib_test.test_case_utils.integer_matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Arrangement, ParseExpectation, \
    ExecutionExpectation, Expectation, arrangement_w_tcds
from exactly_lib_test.test_case_utils.string_matcher.num_lines.test_resources import \
    InstructionArgumentsVariantConstructor, TestCaseBase
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as args
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _NumLinesMatchesWithOperandAsSymbolReference(),
        _TestReferenceToIntegerMatcher(),
        _TestIntegerMatcherShouldBeParsedAsSimpleExpression(),
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
        operand_symbol = StringSymbolContext.of_constant('operand_symbol',
                                                         actual_number_of_lines)

        symbol_table_with_operand_symbol = operand_symbol.symbol_table

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
            expected_symbol_references=expected_symbol_usages,
        )


class _TestReferenceToIntegerMatcher(unittest.TestCase):
    def runTest(self):
        lines = ['1',
                 '2',
                 '3']
        actual_number_of_lines = len(lines)

        integer_matcher = IntegerMatcherSymbolContext.of_primitive(
            'INTEGER_MATCHER',
            matchers.matcher(
                comparators.EQ,
                actual_number_of_lines,
            )
        )
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            args.NumLines(integer_matcher.name__sym_ref_syntax).as_remaining_source,
            integration_check.model_of(lines_content(lines)),
            arrangement_w_tcds(
                symbols=integer_matcher.symbol_table,
            ),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_end_of_line(1),
                    symbol_references=integer_matcher.references_assertion,
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                ),
            ),
        )


class _TestIntegerMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        after_lhs_expression = logic.AND_OPERATOR_NAME + ' after bin op'
        integer_matcher = IntegerMatcherSymbolContextOfPrimitiveConstant(
            'MATCHER_SYMBOL',
            True,
        )
        complex_expression = ' '.join((integer_matcher.name__sym_ref_syntax,
                                       after_lhs_expression))
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            args.NumLines(complex_expression).as_remaining_source,
            integration_check.arbitrary_model(),
            arrangement_w_tcds(
                symbols=integer_matcher.symbol_table,
            ),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_line(
                        current_line_number=1,
                        remaining_part_of_current_line=after_lhs_expression,
                    ),
                    symbol_references=integer_matcher.references_assertion,
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(integer_matcher.result_value)
                ),
            ),
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
            is_reference_to_symbol_in_expression(operand_symbol.name)
        ])

        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(
                operator=comparators.GTE.name,
                operand=expression_that_evaluates_to_actual_number_of_lines),
            expected_result_of_positive_test=PassOrFail.PASS,
            actual_file_contents=actual_contents,
            symbols=symbol_table_with_operand_symbol,
            expected_symbol_references=expected_symbol_usages,
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
                    integration_check.arbitrary_model(),
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
                            validation=case.assertions,
                        ),
                    )
                )
