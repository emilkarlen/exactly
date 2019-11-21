import unittest
from typing import List

from exactly_lib.test_case_utils.line_matcher import line_matchers as sut
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.test_resources import matcher_combinators_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAnd),
        unittest.makeSuite(TestOr),
        unittest.makeSuite(TestNot),
    ])


def constant_matcher_with_custom_name(name: str, result: bool) -> LineMatcher:
    return matchers.ConstantMatcherWithCustomName(name, result)


class LineMatcherConfiguration(matcher_combinators_check.MatcherConfiguration):
    def irrelevant_model(self):
        return 69, 'irrelevant line model'

    def matcher_with_constant_result(self,
                                     name: str,
                                     result: bool) -> LineMatcher:
        return constant_matcher_with_custom_name(name, result)

    def matcher_that_registers_model_argument_and_returns_constant(self, registry: List, result: bool) -> LineMatcher:
        return matchers.MatcherThatRegistersModelArgument(registry, result)


class TestAnd(matcher_combinators_check.TestAndBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return LineMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return sut.conjunction(constructor_argument)


class TestOr(matcher_combinators_check.TestOrBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return LineMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return sut.disjunction(constructor_argument)


class TestNot(matcher_combinators_check.TestNotBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return LineMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return sut.negation(constructor_argument)
