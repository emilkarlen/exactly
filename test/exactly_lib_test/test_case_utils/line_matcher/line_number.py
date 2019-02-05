import unittest

from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcherFromComparisonOperator
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherLineNumber
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_utils.condition.integer.test_resources.arguments_building import int_condition__expr
from exactly_lib_test.test_case_utils.condition.integer.test_resources.integer_resolver import \
    is_reference_to_symbol_in_expression
from exactly_lib_test.test_case_utils.condition.integer.test_resources.validation_cases import \
    failing_integer_validation_cases
from exactly_lib_test.test_case_utils.line_matcher.test_resources import arguments_building as arg, integration_check
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(Test),
        _SymbolReferencesInOperandShouldBeReported(),
        _ValidationPreSdsShouldFailWhenOperandIsNotExpressionThatEvaluatesToAnInteger(),
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


class Test(unittest.TestCase):
    def test_option_description_SHOULD_be_a_string(self):
        # ARRANGE #
        integer_matcher = IntegerMatcherFromComparisonOperator('the name of lhs',
                                                               comparators.EQ,
                                                               69 + 72)
        a_matcher = LineMatcherLineNumber(integer_matcher)

        # ACT #

        actual = a_matcher.option_description

        # ASSERT #

        self.assertIsInstance(actual, str)

    def test_match(self):
        # ARRANGE #
        cases = [
            Case(actual_lhs=5,
                 operator=comparators.EQ,
                 constant_rhs=5,
                 expected=True),

            Case(actual_lhs=6,
                 operator=comparators.EQ,
                 constant_rhs=5,
                 expected=False),

            Case(actual_lhs=4,
                 operator=comparators.LT,
                 constant_rhs=5,
                 expected=True),
        ]

        for case in cases:
            with self.subTest(actual_lhs=case.actual_lhs,
                              operator=case.operator.name,
                              constant_rhs=case.constant_rhs):
                matcher = matcher_of(case.operator, case.constant_rhs)
                line = (case.actual_lhs, 'irrelevant line contents')
                # ACT #

                actual = matcher.matches(line)

                # ASSERT #

                self.assertEqual(case.expected, actual)


class _ValidationPreSdsShouldFailWhenOperandIsNotExpressionThatEvaluatesToAnInteger(unittest.TestCase):
    def runTest(self):
        for case in failing_integer_validation_cases():
            with self.subTest(invalid_value=case.case_name):
                arguments = arg.LineNum(int_condition__expr(comparators.EQ, case.integer_expr_string))
                integration_check.check(
                    self,
                    source=
                    remaining_source(str(arguments)),
                    model=_ARBITRARY_MODEL,
                    arrangement=
                    integration_check.Arrangement(
                        symbols=case.symbol_table
                    ),
                    expectation=
                    integration_check.Expectation(
                        symbol_references=case.symbol_references_expectation,
                        validation=case.expectation,
                    )
                )


class _SymbolReferencesInOperandShouldBeReported(unittest.TestCase):
    def runTest(self):
        actual_line_num = 3
        int_string_symbol = NameAndValue(
            'int_string_symbol_name',
            string_resolvers.str_constant(str(actual_line_num))
        )

        arguments = arg.LineNum(int_condition__expr(comparators.EQ,
                                                    symbol_reference_syntax_for_name(int_string_symbol.name)))

        model_that_matches = (actual_line_num, 'the line')

        integration_check.check(
            self,
            source=
            remaining_source(str(arguments)),
            model=model_that_matches,
            arrangement=
            integration_check.Arrangement(
                symbols=symbol_utils.symbol_table_from_name_and_resolvers([int_string_symbol])
            ),
            expectation=
            integration_check.Expectation(
                symbol_references=asrt.matches_sequence([
                    is_reference_to_symbol_in_expression(int_string_symbol.name)
                ]),
            )

        )


def matcher_of(operator: comparators.ComparisonOperator,
               constant_rhs: int) -> LineMatcherLineNumber:
    return LineMatcherLineNumber(
        IntegerMatcherFromComparisonOperator('the name of lhs',
                                             operator,
                                             constant_rhs))


_ARBITRARY_MODEL = (1, 'arbitrary model line')
