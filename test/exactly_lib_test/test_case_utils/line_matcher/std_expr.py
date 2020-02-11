import unittest
from typing import Callable

from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv, MatcherTypeSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatchingResult
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.line_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.test_case_utils.matcher.test_resources.std_expr import test_cases
from exactly_lib_test.test_case_utils.matcher.test_resources.std_expr.configuration import MatcherConfiguration


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstant),
        unittest.makeSuite(TestSymbolReference),
        unittest.makeSuite(TestParenthesis),
        unittest.makeSuite(TestNegation),
        unittest.makeSuite(TestConjunction),
        unittest.makeSuite(TestDisjunction),
        unittest.makeSuite(TestPrecedence),
    ])


class LineMatcherConfiguration(MatcherConfiguration[LineMatcherLine]):
    def mk_logic_type(self, generic: MatcherSdv[LineMatcherLine]) -> MatcherTypeSdv[LineMatcherLine]:
        return LineMatcherSdv(generic)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.LINE_MATCHER

    def parser(self) -> Parser[MatcherTypeSdv[LineMatcherLine]]:
        return parse_line_matcher.parser()

    def checker(self) -> IntegrationChecker[MatcherWTraceAndNegation[LineMatcherLine],
                                            Callable[[FullResolvingEnvironment], LineMatcherLine],
                                            MatchingResult]:
        return integration_check.CHECKER

    def arbitrary_model(self, environment: FullResolvingEnvironment) -> LineMatcherLine:
        return 69, 'arbitrary line model'


_LINE_MATCHER_CONFIGURATION = LineMatcherConfiguration()


class _WithConfiguration:
    @property
    def configuration(self) -> MatcherConfiguration[LineMatcherLine]:
        return _LINE_MATCHER_CONFIGURATION


class TestConstant(_WithConfiguration, test_cases.TestConstantBase[LineMatcherLine]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestParenthesis(_WithConfiguration, test_cases.TestParenthesisBase[LineMatcherLine]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSymbolReference(_WithConfiguration, test_cases.TestSymbolReferenceBase[LineMatcherLine]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestNegation(_WithConfiguration, test_cases.TestNegationBase[LineMatcherLine]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestConjunction(_WithConfiguration, test_cases.TestConjunctionBase[LineMatcherLine]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestDisjunction(_WithConfiguration, test_cases.TestDisjunctionBase[LineMatcherLine]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestPrecedence(_WithConfiguration, test_cases.TestPrecedence[LineMatcherLine]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass
