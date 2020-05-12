import pathlib
import unittest
from typing import Callable

from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatchingResult
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherSymbolValueContext, FileMatcherSymbolContext
from exactly_lib_test.test_case_utils.file_matcher.test_resources import file_matcher_models as models
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
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


class FileMatcherConfiguration(MatcherConfiguration[FileMatcherModel]):
    def mk_logic_type_value_context_of_primitive(self,
                                                 primitive: MatcherWTraceAndNegation[FileMatcherModel]
                                                 ) -> FileMatcherSymbolValueContext:
        return FileMatcherSymbolValueContext.of_primitive(primitive)

    def mk_logic_type_context_of_primitive(self,
                                           name: str,
                                           primitive: MatcherWTraceAndNegation[FileMatcherModel]
                                           ) -> FileMatcherSymbolContext:
        return FileMatcherSymbolContext.of_primitive(name, primitive)

    def mk_logic_type_context_of_sdv(self,
                                     name: str,
                                     sdv: MatcherSdv[FileMatcherModel]
                                     ) -> FileMatcherSymbolContext:
        return FileMatcherSymbolContext.of_sdv(name, sdv)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.FILE_MATCHER

    def parser(self) -> Parser[MatcherSdv[FileMatcherModel]]:
        return parse_file_matcher.parser()

    def checker(self) -> IntegrationChecker[MatcherWTraceAndNegation[FileMatcherModel],
                                            Callable[[FullResolvingEnvironment], FileMatcherModel],
                                            MatchingResult]:
        return integration_check.CHECKER

    def arbitrary_model(self, environment: FullResolvingEnvironment) -> FileMatcherModel:
        return models.new_model(pathlib.Path('arbitrary path'))


_FILE_MATCHER_CONFIGURATION = FileMatcherConfiguration()


class _WithConfiguration:
    @property
    def configuration(self) -> MatcherConfiguration[FileMatcherModel]:
        return _FILE_MATCHER_CONFIGURATION


class TestConstant(_WithConfiguration, test_cases.TestConstantBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestParenthesis(_WithConfiguration, test_cases.TestParenthesisBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSymbolReference(_WithConfiguration, test_cases.TestSymbolReferenceBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestNegation(_WithConfiguration, test_cases.TestNegationBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestConjunction(_WithConfiguration, test_cases.TestConjunctionBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestDisjunction(_WithConfiguration, test_cases.TestDisjunctionBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestPrecedence(_WithConfiguration, test_cases.TestPrecedence[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass
