import unittest
from typing import List

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name, SymbolWithReferenceSyntax
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_utils.condition.integer.test_resources.arguments_building import int_condition__expr
from exactly_lib_test.test_case_utils.condition.integer.test_resources.integer_sdv import \
    is_reference_to_symbol_in_expression
from exactly_lib_test.test_case_utils.condition.integer.test_resources.validation_cases import \
    failing_integer_validation_cases
from exactly_lib_test.test_case_utils.line_matcher.test_resources import arguments_building as arg
from exactly_lib_test.test_case_utils.line_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.line_matcher.test_resources.integration_check import ARBITRARY_MODEL
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import main_result_is_success, \
    main_result_is_failure, ExecutionExpectation, ParseExpectation
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _SymbolReferencesInOperandShouldBeReported(),
        _ValidationPreSdsShouldFailWhenOperandIsNotExpressionThatEvaluatesToAnInteger(),
        _ParseAndMatchTest(),
    ])


class Case:
    def __init__(self,
                 actual_lhs: int,
                 operator: comparators.ComparisonOperator,
                 constant_rhs: int,
                 expected: bool):
        self.actual_lhs = actual_lhs
        self.operator = operator
        self.constant_rhs = constant_rhs
        self.expected = expected


class IntegrationCheckCase:
    def __init__(self,
                 name: str,
                 line_num_of_model: int,
                 operator: comparators.ComparisonOperator,
                 int_expr: str,
                 result: ValueAssertion[MatchingResult],
                 symbols: List[NameAndValue[SymbolDependentValue]]):
        self.name = name
        self.line_num_of_model = line_num_of_model
        self.operator = operator
        self.int_expr = int_expr
        self.result = result
        self.symbols = symbols


class _ValidationPreSdsShouldFailWhenOperandIsNotExpressionThatEvaluatesToAnInteger(unittest.TestCase):
    def runTest(self):
        for case in failing_integer_validation_cases():
            with self.subTest(invalid_value=case.case_name):
                arguments = arg.LineNum(int_condition__expr(comparators.EQ, case.integer_expr_string))
                integration_check.check(
                    self,
                    source=
                    remaining_source(str(arguments)),
                    model_constructor=ARBITRARY_MODEL,
                    arrangement=
                    case.symbol_table,
                    expectation=
                    integration_check.Expectation(
                        ParseExpectation(
                            symbol_references=case.symbol_references_expectation,
                        ),
                        ExecutionExpectation(
                            validation=case.expectation,
                        ),
                    )
                )


class _SymbolReferencesInOperandShouldBeReported(unittest.TestCase):
    def runTest(self):
        actual_line_num = 3
        int_string_symbol = NameAndValue(
            'int_string_symbol_name',
            string_sdvs.str_constant(str(actual_line_num))
        )

        arguments = arg.LineNum(int_condition__expr(comparators.EQ,
                                                    symbol_reference_syntax_for_name(int_string_symbol.name)))

        model_that_matches = integration_check.constant_model((actual_line_num, 'the line'))

        integration_check.check(
            self,
            source=
            remaining_source(str(arguments)),
            model_constructor=model_that_matches,
            arrangement=
            symbol_utils.symbol_table_from_name_and_sdvs([int_string_symbol]),
            expectation=
            integration_check.Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        is_reference_to_symbol_in_expression(int_string_symbol.name)
                    ]),
                ),
            )

        )


class _ParseAndMatchTest(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        symbol_1 = SymbolWithReferenceSyntax('symbol_1')
        symbol_2 = SymbolWithReferenceSyntax('symbol_2')

        cases = (
                successful_and_unsuccessful(
                    'constant single integer expression',
                    line_num_of_model=72,
                    successful_operator=comparators.EQ,
                    unsuccessful_operator=comparators.NE,
                    int_expr='72',
                    symbols=[]
                )
                +
                successful_and_unsuccessful(
                    'constant complex expression',
                    line_num_of_model=10,
                    successful_operator=comparators.EQ,
                    unsuccessful_operator=comparators.GT,
                    int_expr='1+4+5',
                    symbols=[]
                )
                +
                successful_and_unsuccessful(
                    'just one symbol reference with integer constant',
                    line_num_of_model=72,
                    successful_operator=comparators.EQ,
                    unsuccessful_operator=comparators.NE,
                    int_expr=str(symbol_1),
                    symbols=[
                        NameAndValue(symbol_1.name, string_sdvs.str_constant('72'))
                    ]
                )
                +
                successful_and_unsuccessful(
                    'multiple symbols with python functions and operator in symbol value',
                    line_num_of_model=13,
                    successful_operator=comparators.EQ,
                    unsuccessful_operator=comparators.NE,
                    int_expr='len({}){}'.format(
                        symbol_1,
                        symbol_2
                    ),
                    symbols=[
                        NameAndValue(symbol_1.name, string_sdvs.str_constant('"abc"')),
                        NameAndValue(symbol_2.name, string_sdvs.str_constant('+(20-10)')),
                    ]
                )
        )

        for case in cases:
            arguments = arg.LineNum(int_condition__expr(case.operator,
                                                        case.int_expr))
            expected_symbol_references = asrt.matches_sequence([
                is_reference_to_symbol_in_expression(symbol.name)
                for symbol in case.symbols
            ])

            # ACT & ASSERT #

            with self.subTest(case.name):
                integration_check.check(
                    self,
                    remaining_source(str(arguments)),
                    integration_check.constant_model((case.line_num_of_model, 'ignored line text')),
                    symbol_utils.symbol_table_from_name_and_sdvs(case.symbols),
                    integration_check.Expectation(
                        ParseExpectation(
                            symbol_references=expected_symbol_references,
                        ),
                        ExecutionExpectation(
                            main_result=case.result
                        ),
                    )
                )


def successful_and_unsuccessful(name: str,
                                line_num_of_model: int,
                                successful_operator: comparators.ComparisonOperator,
                                unsuccessful_operator: comparators.ComparisonOperator,
                                int_expr: str,
                                symbols: List[NameAndValue[SymbolDependentValue]]) -> List[IntegrationCheckCase]:
    return [
        IntegrationCheckCase(
            name + '/successful: ' + successful_operator.name,
            line_num_of_model,
            successful_operator,
            int_expr,
            main_result_is_success(),
            symbols,
        ),
        IntegrationCheckCase(
            name + '/unsuccessful: ' + unsuccessful_operator.name,
            line_num_of_model,
            unsuccessful_operator,
            int_expr,
            main_result_is_failure(),
            symbols,
        ),
    ]
