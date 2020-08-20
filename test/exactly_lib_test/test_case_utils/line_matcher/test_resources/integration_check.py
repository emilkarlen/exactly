import unittest
from typing import Callable, Optional

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Expectation, arrangement_wo_tcds
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check as matcher_integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.matcher_checker import \
    MatcherPropertiesConfiguration
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments

ModelConstructor = Callable[[FullResolvingEnvironment], LineMatcherLine]

ARBITRARY_MODEL = matcher_integration_check.constant_model((1, 'arbitrary model line'))


def constant_model(model: LineMatcherLine) -> ModelConstructor:
    return matcher_integration_check.constant_model(model)


CHECKER = integration_check.IntegrationChecker(
    parse_line_matcher.parsers(True).full,
    MatcherPropertiesConfiguration(),
    False,
)


def check(put: unittest.TestCase,
          source: ParseSource,
          model_constructor: ModelConstructor,
          arrangement: Optional[SymbolTable] = None,
          expectation: Expectation = Expectation()):
    CHECKER.check(put,
                  source,
                  model_constructor,
                  arrangement_wo_tcds(arrangement),
                  expectation,
                  )


def check_with_source_variants(put: unittest.TestCase,
                               arguments: Arguments,
                               model_constructor: ModelConstructor,
                               arrangement: Optional[SymbolTable] = None,
                               expectation: Expectation = Expectation()):
    CHECKER.check__w_source_variants(put,
                                     arguments,
                                     model_constructor,
                                     arrangement_wo_tcds(arrangement),
                                     expectation,
                                     )
