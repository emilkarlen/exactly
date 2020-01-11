import unittest

from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils.line_matcher import line_matchers as sut, parse_line_matcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.line_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import MatcherChecker
from exactly_lib_test.test_case_utils.test_resources import matcher_combinators_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSymbolReference),
        unittest.makeSuite(TestAnd),
        unittest.makeSuite(TestOr),
        unittest.makeSuite(TestNot),
    ])


def constant_matcher_with_custom_name(name: str, result: bool) -> LineMatcher:
    return matchers.ConstantMatcherWithCustomName(name, result)


class LineMatcherConfiguration(matcher_combinators_check.MatcherConfiguration[LineMatcherLine]):
    def mk_logic_type(self, generic: MatcherSdv[LineMatcherLine]) -> MatcherTypeSdv[LineMatcherLine]:
        return LineMatcherSdv(generic)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.LINE_MATCHER

    def parser(self) -> Parser[MatcherTypeSdv[LineMatcherLine]]:
        return parse_line_matcher.parser()

    def checker(self) -> MatcherChecker[LineMatcherLine]:
        return integration_check.CHECKER

    def irrelevant_model(self) -> LineMatcherLine:
        return 69, 'irrelevant line model'


_LINE_MATCHER_CONFIGURATION = LineMatcherConfiguration()


class TestSymbolReference(matcher_combinators_check.TestSymbolReferenceBase[LineMatcherLine]):
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration[LineMatcherLine]:
        return _LINE_MATCHER_CONFIGURATION


class TestAnd(matcher_combinators_check.TestAndBase[LineMatcherLine]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration[LineMatcherLine]:
        return _LINE_MATCHER_CONFIGURATION

    def new_combinator_to_check(self, constructor_argument) -> MatcherWTrace[LineMatcherLine]:
        return sut.conjunction(constructor_argument)


class TestOr(matcher_combinators_check.TestOrBase[LineMatcherLine]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration[LineMatcherLine]:
        return _LINE_MATCHER_CONFIGURATION

    def new_combinator_to_check(self, constructor_argument) -> MatcherWTrace[LineMatcherLine]:
        return sut.disjunction(constructor_argument)


class TestNot(matcher_combinators_check.TestNotBase[LineMatcherLine]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration[LineMatcherLine]:
        return _LINE_MATCHER_CONFIGURATION

    def new_combinator_to_check(self, constructor_argument) -> MatcherWTrace[LineMatcherLine]:
        return sut.negation(constructor_argument)
