import unittest

from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.type_system.logic.string_matcher import FileToCheck, GenericStringMatcherSdv
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import MatcherChecker
from exactly_lib_test.test_case_utils.matcher.test_resources.std_expr import test_cases
from exactly_lib_test.test_case_utils.matcher.test_resources.std_expr.configuration import MatcherConfiguration
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSymbolReference),
        unittest.makeSuite(TestParenthesis),
        unittest.makeSuite(TestNegation),
        unittest.makeSuite(TestConjunction),
        unittest.makeSuite(TestDisjunction),
        unittest.makeSuite(TestPrecedence),
    ])


class StringMatcherConfiguration(MatcherConfiguration[FileToCheck]):
    def mk_logic_type(self, generic: GenericStringMatcherSdv) -> MatcherTypeSdv[FileToCheck]:
        return StringMatcherSdv(generic)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.STRING_MATCHER

    def parser(self) -> Parser[MatcherTypeSdv[FileToCheck]]:
        return parse_string_matcher.string_matcher_parser()

    def checker(self) -> MatcherChecker[FileToCheck]:
        return integration_check.CHECKER

    def arbitrary_model(self, environment: FullResolvingEnvironment) -> FileToCheck:
        return integration_check.MODEL_THAT_MUST_NOT_BE_USED


_STRING_MATCHER_CONFIGURATION = StringMatcherConfiguration()


class _WithConfiguration:
    @property
    def configuration(self) -> MatcherConfiguration[FileToCheck]:
        return _STRING_MATCHER_CONFIGURATION


class TestParenthesis(_WithConfiguration, test_cases.TestParenthesis[FileToCheck]):
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
