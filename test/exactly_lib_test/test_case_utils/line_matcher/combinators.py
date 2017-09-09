import unittest

from exactly_lib.test_case_utils.line_matcher import line_matchers as sut
from exactly_lib_test.test_case_utils.test_resources import matcher_combinators_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAnd),
        unittest.makeSuite(TestOr),
        unittest.makeSuite(TestNot),
    ])


class LineMatcherConfiguration(matcher_combinators_check.MatcherConfiguration):
    def irrelevant_model(self):
        return 'irrelevant line model'

    def matcher_with_constant_result(self, result: bool):
        return sut.LineMatcherConstant(result)

    def matcher_that_registers_model_argument_and_returns_constant(self, result: bool
                                                                   ) -> matcher_combinators_check.MatcherThatRegistersModelArgument:
        return LineMatcherThatRegistersModelArgument(result)


class TestAnd(matcher_combinators_check.TestAndBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return LineMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return sut.LineMatcherAnd(constructor_argument)


class TestOr(matcher_combinators_check.TestOrBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return LineMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return sut.LineMatcherOr(constructor_argument)


class TestNot(matcher_combinators_check.TestNotBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return LineMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return sut.LineMatcherNot(constructor_argument)


class LineMatcherThatRegistersModelArgument(sut.LineMatcher,
                                            matcher_combinators_check.MatcherThatRegistersModelArgument):
    def matches(self, line: str) -> bool:
        self.register_argument(line)
        return self._constant_result
