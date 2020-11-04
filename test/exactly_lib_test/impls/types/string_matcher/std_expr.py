import unittest
from typing import Callable

from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.string_matcher import parse_string_matcher
from exactly_lib.symbol.value_type import LogicValueType
from exactly_lib.type_val_deps.dep_variants.sdv.matcher import MatcherSdv
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib_test.impls.types.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.impls.types.matcher.test_resources.std_expr import test_cases
from exactly_lib_test.impls.types.matcher.test_resources.std_expr.configuration import MatcherConfiguration
from exactly_lib_test.impls.types.string_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.string_models.test_resources import model_constructor
from exactly_lib_test.type_val_deps.types.test_resources.string_matcher import StringMatcherSymbolValueContext, \
    StringMatcherSymbolContext


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


class StringMatcherConfiguration(MatcherConfiguration[StringModel]):
    def mk_logic_type_value_context_of_primitive(self,
                                                 primitive: MatcherWTrace[StringModel]
                                                 ) -> StringMatcherSymbolValueContext:
        return StringMatcherSymbolValueContext.of_primitive(primitive)

    def mk_logic_type_context_of_primitive(self,
                                           name: str,
                                           primitive: MatcherWTrace[StringModel]
                                           ) -> StringMatcherSymbolContext:
        return StringMatcherSymbolContext.of_primitive(name, primitive)

    def mk_logic_type_context_of_sdv(self,
                                     name: str,
                                     sdv: MatcherSdv[StringModel]
                                     ) -> StringMatcherSymbolContext:
        return StringMatcherSymbolContext.of_sdv(name, sdv)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.STRING_MATCHER

    def parsers_for_expr_on_any_line(self) -> GrammarParsers[MatcherSdv[StringModel]]:
        return parse_string_matcher.parsers()

    def checker_for_parser_of_full_expr(self) -> IntegrationChecker[MatcherWTrace[StringModel],
                                                                    Callable[[FullResolvingEnvironment], StringModel],
                                                                    MatchingResult]:
        return integration_check.CHECKER__PARSE_FULL

    def arbitrary_model(self, environment: FullResolvingEnvironment) -> StringModel:
        return model_constructor.must_not_be_used(environment)


_STRING_MATCHER_CONFIGURATION = StringMatcherConfiguration()


class _WithConfiguration:
    @property
    def configuration(self) -> MatcherConfiguration[StringModel]:
        return _STRING_MATCHER_CONFIGURATION


class TestConstant(_WithConfiguration, test_cases.TestConstantBase[StringModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestParenthesis(_WithConfiguration, test_cases.TestParenthesisBase[StringModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSymbolReference(_WithConfiguration, test_cases.TestSymbolReferenceBase[StringModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestNegation(_WithConfiguration, test_cases.TestNegationBase[StringModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestConjunction(_WithConfiguration, test_cases.TestConjunctionBase[StringModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestDisjunction(_WithConfiguration, test_cases.TestDisjunctionBase[StringModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestPrecedence(_WithConfiguration, test_cases.TestPrecedence[StringModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass
