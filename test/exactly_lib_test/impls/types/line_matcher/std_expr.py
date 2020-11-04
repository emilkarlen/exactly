import unittest
from typing import Callable

from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.line_matcher import parse_line_matcher
from exactly_lib.symbol.value_type import LogicValueType
from exactly_lib.type_val_deps.dep_variants.sdv.matcher import MatcherSdv
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.line_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.impls.types.matcher.test_resources.std_expr import test_cases
from exactly_lib_test.impls.types.matcher.test_resources.std_expr.configuration import MatcherConfiguration
from exactly_lib_test.type_val_deps.types.test_resources.line_matcher import LineMatcherSymbolValueContext, \
    LineMatcherSymbolContext


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
    def mk_logic_type_value_context_of_primitive(self,
                                                 primitive: MatcherWTrace[LineMatcherLine]
                                                 ) -> LineMatcherSymbolValueContext:
        return LineMatcherSymbolValueContext.of_primitive(primitive)

    def mk_logic_type_context_of_primitive(self,
                                           name: str,
                                           primitive: MatcherWTrace[LineMatcherLine]
                                           ) -> LineMatcherSymbolContext:
        return LineMatcherSymbolContext.of_primitive(name, primitive)

    def mk_logic_type_context_of_sdv(self,
                                     name: str,
                                     sdv: MatcherSdv[LineMatcherLine]
                                     ) -> LineMatcherSymbolContext:
        return LineMatcherSymbolContext.of_sdv(name, sdv)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.LINE_MATCHER

    def parsers_for_expr_on_any_line(self) -> GrammarParsers[MatcherSdv[LineMatcherLine]]:
        return parse_line_matcher.parsers()

    def checker_for_parser_of_full_expr(self) -> IntegrationChecker[MatcherWTrace[LineMatcherLine],
                                                                    Callable[
                                                                        [FullResolvingEnvironment], LineMatcherLine],
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
