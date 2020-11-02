import unittest
from typing import Optional

from exactly_lib.impls.types.line_matcher import parse_line_matcher
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.line_matcher.test_resources.models import ModelConstructor
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Expectation, arrangement_wo_tcds
from exactly_lib_test.impls.types.matcher.test_resources.matcher_checker import \
    MatcherPropertiesConfiguration
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments

CHECKER = integration_check.IntegrationChecker(
    parse_line_matcher.parsers(True).full,
    MatcherPropertiesConfiguration(),
    False,
)

CHECKER__PARSE_SIMPLE = integration_check.IntegrationChecker(
    parse_line_matcher.parsers(True).simple,
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
