import pathlib
import unittest
from typing import Callable

from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.file_matcher import parse_file_matcher
from exactly_lib.symbol.value_type import LogicValueType
from exactly_lib.type_val_deps.dep_variants.sdv.matcher_sdv import MatcherSdv
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.file_matcher.test_resources import file_matcher_models as models
from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.impls.types.matcher.test_resources.std_expr import test_cases
from exactly_lib_test.impls.types.matcher.test_resources.std_expr.configuration import MatcherConfiguration
from exactly_lib_test.type_val_deps.types.test_resources.file_matcher import FileMatcherSymbolValueContext, \
    FileMatcherSymbolContext


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
                                                 primitive: MatcherWTrace[FileMatcherModel]
                                                 ) -> FileMatcherSymbolValueContext:
        return FileMatcherSymbolValueContext.of_primitive(primitive)

    def mk_logic_type_context_of_primitive(self,
                                           name: str,
                                           primitive: MatcherWTrace[FileMatcherModel]
                                           ) -> FileMatcherSymbolContext:
        return FileMatcherSymbolContext.of_primitive(name, primitive)

    def mk_logic_type_context_of_sdv(self,
                                     name: str,
                                     sdv: MatcherSdv[FileMatcherModel]
                                     ) -> FileMatcherSymbolContext:
        return FileMatcherSymbolContext.of_sdv(name, sdv)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.FILE_MATCHER

    def parsers_for_expr_on_any_line(self) -> GrammarParsers[MatcherSdv[FileMatcherModel]]:
        return parse_file_matcher.parsers()

    def checker_for_parser_of_full_expr(self) -> IntegrationChecker[MatcherWTrace[FileMatcherModel],
                                                                    Callable[
                                                                        [FullResolvingEnvironment], FileMatcherModel],
                                                                    MatchingResult]:
        return integration_check.CHECKER__PARSE_FULL

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
