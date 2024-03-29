import unittest
from typing import Callable

from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.integer_matcher import parse_integer_matcher
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.integer_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.impls.types.matcher.test_resources.std_expr import test_cases
from exactly_lib_test.impls.types.matcher.test_resources.std_expr.configuration import MatcherConfiguration
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.symbol_context import \
    IntegerMatcherSymbolContext, IntegerMatcherSymbolValueContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstant),
        unittest.makeSuite(TestSymbolReference),
        unittest.makeSuite(TestParentheses),
        unittest.makeSuite(TestNegation),
        unittest.makeSuite(TestConjunction),
        unittest.makeSuite(TestDisjunction),
        unittest.makeSuite(TestPrecedence),
    ])


class IntegerMatcherConfiguration(MatcherConfiguration[int]):
    def mk_logic_type_value_context_of_primitive(self,
                                                 primitive: MatcherWTrace[int]
                                                 ) -> IntegerMatcherSymbolValueContext:
        return IntegerMatcherSymbolValueContext.of_primitive(primitive)

    def mk_logic_type_context_of_primitive(self,
                                           name: str,
                                           primitive: MatcherWTrace[int]
                                           ) -> IntegerMatcherSymbolContext:
        return IntegerMatcherSymbolContext.of_primitive(name, primitive)

    def mk_logic_type_context_of_sdv(self,
                                     name: str,
                                     sdv: MatcherSdv[int]
                                     ) -> IntegerMatcherSymbolContext:
        return IntegerMatcherSymbolContext.of_sdv(name, sdv)

    def value_type(self) -> ValueType:
        return ValueType.INTEGER_MATCHER

    def parsers_for_expr_on_any_line(self) -> GrammarParsers[MatcherSdv[int]]:
        return parse_integer_matcher.parsers()

    def checker_for_parser_of_full_expr(self) -> IntegrationChecker[MatcherWTrace[int],
                                                                    Callable[
                                                                        [FullResolvingEnvironment], int],
                                                                    MatchingResult]:
        return integration_check.CHECKER__PARSE_FULL

    def arbitrary_model(self, environment: FullResolvingEnvironment) -> int:
        return integration_check.ARBITRARY_MODEL


_INTEGER_MATCHER_CONFIGURATION = IntegerMatcherConfiguration()


class _WithConfiguration:
    @property
    def configuration(self) -> MatcherConfiguration[int]:
        return _INTEGER_MATCHER_CONFIGURATION


class TestConstant(_WithConfiguration, test_cases.TestConstantBase[int]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestParentheses(_WithConfiguration, test_cases.TestParenthesesBase[int]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSymbolReference(_WithConfiguration, test_cases.TestSymbolReferenceBase[int]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestNegation(_WithConfiguration, test_cases.TestNegationBase[int]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestConjunction(_WithConfiguration, test_cases.TestConjunctionBase[int]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestDisjunction(_WithConfiguration, test_cases.TestDisjunctionBase[int]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestPrecedence(_WithConfiguration, test_cases.TestPrecedence[int]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass
