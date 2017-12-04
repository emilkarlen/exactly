import unittest

from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcherFromComparisonOperator
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherLineNumber


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


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


def matcher_of(operator: comparators.ComparisonOperator,
               constant_rhs: int) -> LineMatcherLineNumber:
    return LineMatcherLineNumber(
        IntegerMatcherFromComparisonOperator('the name of lhs',
                                             operator,
                                             constant_rhs))
