import unittest
from typing import List

from exactly_lib.definitions import logic
from exactly_lib.impls.types.condition import comparators
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name, SymbolWithReferenceSyntax
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.integer.test_resources.arguments_building import int_condition__expr
from exactly_lib_test.impls.types.integer.test_resources.integer_sdv import \
    is_reference_to_symbol_in_expression
from exactly_lib_test.impls.types.integer.test_resources.validation_cases import \
    failing_integer_validation_cases
from exactly_lib_test.impls.types.line_matcher.test_resources import arguments_building as arg
from exactly_lib_test.impls.types.line_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.line_matcher.test_resources import models
from exactly_lib_test.impls.types.line_matcher.test_resources.models import ARBITRARY_MODEL
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ParseExpectation, ExecutionExpectation, \
    Expectation, arrangement_wo_tcds
from exactly_lib_test.impls.types.matcher.test_resources.assertions import main_result_is_success, \
    main_result_is_failure
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext, \
    StringIntConstantSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.integer_matcher import \
    IntegerMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _SymbolReferencesInOperandShouldBeReported(),
        _IntegerMatcherSymbolReferencesShouldBeReported(),
        _IntegerMatcherShouldBeParsedAsSimpleExpression(),
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
                 result: Assertion[MatchingResult],
                 symbols: List[SymbolContext]):
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
                    Expectation(
                        ParseExpectation(
                            symbol_references=case.symbol_references_expectation,
                        ),
                        ExecutionExpectation(
                            validation=case.assertions,
                        ),
                    )
                )


class _SymbolReferencesInOperandShouldBeReported(unittest.TestCase):
    def runTest(self):
        int_string_symbol = StringIntConstantSymbolContext(
            'int_string_symbol_name',
            3
        )

        arguments = arg.LineNum(int_condition__expr(comparators.EQ,
                                                    symbol_reference_syntax_for_name(int_string_symbol.name)))

        model_that_matches = models.constant((int_string_symbol.int_value, 'the line'))

        integration_check.check(
            self,
            source=
            remaining_source(str(arguments)),
            model_constructor=model_that_matches,
            arrangement=
            int_string_symbol.symbol_table,
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        is_reference_to_symbol_in_expression(int_string_symbol.name)
                    ]),
                ),
            )
        )


class _IntegerMatcherSymbolReferencesShouldBeReported(unittest.TestCase):
    def runTest(self):
        matcher_symbol = IntegerMatcherSymbolContextOfPrimitiveConstant(
            'MATCHER_SYMBOL',
            True,
        )

        arguments = arg.LineNum(matcher_symbol.name__sym_ref_syntax)

        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            source=
            arguments.as_remaining_source,
            input_=models.ARBITRARY_MODEL,
            arrangement=arrangement_wo_tcds(
                symbols=matcher_symbol.symbol_table,
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=matcher_symbol.references_assertion,
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(matcher_symbol.result_value)
                )
            )
        )


class _IntegerMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        after_lhs_expression = logic.AND_OPERATOR_NAME + ' after bin op'
        matcher_symbol = IntegerMatcherSymbolContextOfPrimitiveConstant(
            'MATCHER_SYMBOL',
            True,
        )
        complex_expression = ' '.join((matcher_symbol.name__sym_ref_syntax,
                                       after_lhs_expression))
        arguments = arg.LineNum(complex_expression)

        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            source=
            arguments.as_remaining_source,
            input_=models.ARBITRARY_MODEL,
            arrangement=arrangement_wo_tcds(
                symbols=matcher_symbol.symbol_table,
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_line(
                        current_line_number=1,
                        remaining_part_of_current_line=after_lhs_expression,
                    ),
                    symbol_references=matcher_symbol.references_assertion,
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(matcher_symbol.result_value)
                )
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
                        StringSymbolContext.of_constant(symbol_1.name, '72')
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
                        StringSymbolContext.of_constant(symbol_1.name, '"abc"'),
                        StringSymbolContext.of_constant(symbol_2.name, '+(20-10)'),
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
                    models.constant((case.line_num_of_model, 'ignored line text')),
                    SymbolContext.symbol_table_of_contexts(case.symbols),
                    Expectation(
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
                                symbols: List[SymbolContext]) -> List[IntegrationCheckCase]:
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
