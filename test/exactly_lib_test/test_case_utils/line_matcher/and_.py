import unittest

from exactly_lib.test_case_utils.line_matcher import line_matchers as sut
from exactly_lib_test.test_case_utils.test_resources import combinator_matcher_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestAnd)


class LineMatcherConfiguration(combinator_matcher_check.MatcherConfiguration):
    def irrelevant_model(self):
        return 'irrelevant line model'

    def constant(self, result: bool):
        return sut.LineMatcherConstant(result)

    def apply(self, matcher_to_check, model) -> bool:
        assert isinstance(matcher_to_check, sut.LineMatcher)  # Sanity check
        return matcher_to_check.matches(model)

    def matcher_that_registers_model_argument_and_returns_constant(self, result: bool
                                                                   ) -> combinator_matcher_check.MatcherThatRegistersModelArgument:
        return LineMatcherThatRegistersModelArgument(result)


class TestAnd(combinator_matcher_check.TestAndBase):
    @property
    def configuration(self) -> combinator_matcher_check.MatcherConfiguration:
        return LineMatcherConfiguration()

    def mk_and(self, sub_matchers: list):
        return sut.LineMatcherAnd(sub_matchers)


class LineMatcherThatRegistersModelArgument(sut.LineMatcher,
                                            combinator_matcher_check.MatcherThatRegistersModelArgument):
    def matches(self, line: str) -> bool:
        self.register_argument(line)
        return self._constant_result
