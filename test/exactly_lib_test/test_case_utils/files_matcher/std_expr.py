import unittest
from typing import Callable

from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.files_matcher import FilesMatcherStv
from exactly_lib.symbol.logic.matcher import MatcherSdv, MatcherTypeStv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatchingResult
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources import model
from exactly_lib_test.test_case_utils.files_matcher.test_resources.symbol_context import FilesMatcherSymbolValueContext, \
    FilesMatcherSymbolContext
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


class FilesMatcherConfiguration(MatcherConfiguration[FilesMatcherModel]):
    def mk_logic_type(self, generic: MatcherSdv[FilesMatcherModel]) -> MatcherTypeStv[FilesMatcherModel]:
        return FilesMatcherStv(generic)

    def mk_logic_type_value_context_of_primitive(self,
                                                 primitive: MatcherWTraceAndNegation[FilesMatcherModel]
                                                 ) -> FilesMatcherSymbolValueContext:
        return FilesMatcherSymbolValueContext.of_primitive(primitive)

    def mk_logic_type_context_of_primitive(self,
                                           name: str,
                                           primitive: MatcherWTraceAndNegation[FilesMatcherModel]
                                           ) -> FilesMatcherSymbolContext:
        return FilesMatcherSymbolContext.of_primitive(name, primitive)

    def mk_logic_type_context_of_stv(self,
                                     name: str,
                                     stv: MatcherTypeStv[FilesMatcherModel]
                                     ) -> FilesMatcherSymbolContext:
        return FilesMatcherSymbolContext.of_sdtv(name, stv)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.FILES_MATCHER

    def parser(self) -> Parser[MatcherTypeStv[FilesMatcherModel]]:
        return parse_files_matcher.files_matcher_parser()

    def checker(self) -> IntegrationChecker[MatcherWTraceAndNegation[FilesMatcherModel],
                                            Callable[[FullResolvingEnvironment], FilesMatcherModel],
                                            MatchingResult]:
        return integration_check.CHECKER

    def arbitrary_model(self, environment: FullResolvingEnvironment) -> FilesMatcherModel:
        return model.arbitrary_model()(environment)


_FILES_MATCHER_CONFIGURATION = FilesMatcherConfiguration()


class _WithConfiguration:
    @property
    def configuration(self) -> MatcherConfiguration[FileMatcherModel]:
        return _FILES_MATCHER_CONFIGURATION


class TestConstant(_WithConfiguration, test_cases.TestConstantBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSymbolReference(_WithConfiguration, test_cases.TestSymbolReferenceBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestParenthesis(_WithConfiguration, test_cases.TestParenthesisBase[FileMatcherModel]):
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
