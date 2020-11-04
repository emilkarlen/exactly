import unittest
from typing import Callable

from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.files_matcher import parse_files_matcher
from exactly_lib.symbol.value_type import LogicValueType
from exactly_lib.type_val_deps.dep_variants.sdv.matcher import MatcherSdv
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.files_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.files_matcher.test_resources import model
from exactly_lib_test.impls.types.files_matcher.test_resources.symbol_context import FilesMatcherSymbolValueContext, \
    FilesMatcherSymbolContext
from exactly_lib_test.impls.types.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.impls.types.matcher.test_resources.std_expr import test_cases
from exactly_lib_test.impls.types.matcher.test_resources.std_expr.configuration import MatcherConfiguration


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
    def mk_logic_type_value_context_of_primitive(self,
                                                 primitive: MatcherWTrace[FilesMatcherModel]
                                                 ) -> FilesMatcherSymbolValueContext:
        return FilesMatcherSymbolValueContext.of_primitive(primitive)

    def mk_logic_type_context_of_primitive(self,
                                           name: str,
                                           primitive: MatcherWTrace[FilesMatcherModel]
                                           ) -> FilesMatcherSymbolContext:
        return FilesMatcherSymbolContext.of_primitive(name, primitive)

    def mk_logic_type_context_of_sdv(self,
                                     name: str,
                                     sdv: MatcherSdv[FilesMatcherModel]
                                     ) -> FilesMatcherSymbolContext:
        return FilesMatcherSymbolContext.of_sdv(name, sdv)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.FILES_MATCHER

    def parsers_for_expr_on_any_line(self) -> GrammarParsers[MatcherSdv[FilesMatcherModel]]:
        return parse_files_matcher.parsers()

    def checker_for_parser_of_full_expr(self) -> IntegrationChecker[MatcherWTrace[FilesMatcherModel],
                                                                    Callable[
                                                                        [FullResolvingEnvironment], FilesMatcherModel],
                                                                    MatchingResult]:
        return integration_check.CHECKER__PARSE_FULL

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
