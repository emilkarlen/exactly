import unittest
from typing import Callable

from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatchingResult
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherSymbolValueContext, \
    StringMatcherSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.test_case_utils.matcher.test_resources.std_expr import test_cases
from exactly_lib_test.test_case_utils.matcher.test_resources.std_expr.configuration import MatcherConfiguration
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check


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


class StringMatcherConfiguration(MatcherConfiguration[FileToCheck]):
    def mk_logic_type_value_context_of_primitive(self,
                                                 primitive: MatcherWTraceAndNegation[FileToCheck]
                                                 ) -> StringMatcherSymbolValueContext:
        return StringMatcherSymbolValueContext.of_primitive(primitive)

    def mk_logic_type_context_of_primitive(self,
                                           name: str,
                                           primitive: MatcherWTraceAndNegation[FileToCheck]
                                           ) -> StringMatcherSymbolContext:
        return StringMatcherSymbolContext.of_primitive(name, primitive)

    def mk_logic_type_context_of_sdv(self,
                                     name: str,
                                     sdv: MatcherSdv[FileToCheck]
                                     ) -> StringMatcherSymbolContext:
        return StringMatcherSymbolContext.of_sdv(name, sdv)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.STRING_MATCHER

    def parser(self) -> Parser[MatcherSdv[FileToCheck]]:
        return parse_string_matcher.string_matcher_parser()

    def checker(self) -> IntegrationChecker[MatcherWTraceAndNegation[FileToCheck],
                                            Callable[[FullResolvingEnvironment], FileToCheck],
                                            MatchingResult]:
        return integration_check.CHECKER

    def arbitrary_model(self, environment: FullResolvingEnvironment) -> FileToCheck:
        return integration_check.MODEL_THAT_MUST_NOT_BE_USED


_STRING_MATCHER_CONFIGURATION = StringMatcherConfiguration()


class _WithConfiguration:
    @property
    def configuration(self) -> MatcherConfiguration[FileToCheck]:
        return _STRING_MATCHER_CONFIGURATION


class TestConstant(_WithConfiguration, test_cases.TestConstantBase[FileToCheck]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestParenthesis(_WithConfiguration, test_cases.TestParenthesisBase[FileToCheck]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSymbolReference(_WithConfiguration, test_cases.TestSymbolReferenceBase[FileToCheck]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestNegation(_WithConfiguration, test_cases.TestNegationBase[FileToCheck]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestConjunction(_WithConfiguration, test_cases.TestConjunctionBase[FileToCheck]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestDisjunction(_WithConfiguration, test_cases.TestDisjunctionBase[FileToCheck]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestPrecedence(_WithConfiguration, test_cases.TestPrecedence[FileToCheck]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass
