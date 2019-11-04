import unittest

from exactly_lib.test_case_utils.line_matcher import line_matchers as sut
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree import renderers
from exactly_lib_test.test_case_utils.test_resources import matcher_combinators_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAnd),
        unittest.makeSuite(TestOr),
        unittest.makeSuite(TestNot),
    ])


class ConstantMatcherWithCustomName(sut.LineMatcherConstant):
    """Matcher with constant result."""

    def __init__(self, name: str, result: bool):
        super().__init__(result)
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class LineMatcherConfiguration(matcher_combinators_check.MatcherConfiguration):
    def irrelevant_model(self):
        return 69, 'irrelevant line model'

    def matcher_with_constant_result(self,
                                     name: str,
                                     result: bool):
        return ConstantMatcherWithCustomName(name, result)

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


class LineMatcherThatRegistersModelArgument(matcher_combinators_check.MatcherWTraceThatRegistersModelArgument,
                                            sut.LineMatcher):

    def _structure(self) -> StructureRenderer:
        return renderers.header_only(self.name)
