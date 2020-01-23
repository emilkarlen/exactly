import unittest
from typing import Callable, Optional

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Expectation
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments

ModelConstructor = Callable[[FullResolvingEnvironment], LineMatcherLine]

ARBITRARY_MODEL = integration_check.constant_model((1, 'arbitrary model line'))


def constant_model(model: LineMatcherLine) -> ModelConstructor:
    return integration_check.constant_model(model)


CHECKER = integration_check.MatcherChecker(
    parse_line_matcher.parser(),
    LogicValueType.LINE_MATCHER
)


def check(put: unittest.TestCase,
          source: ParseSource,
          model_constructor: ModelConstructor,
          arrangement: Optional[SymbolTable] = None,
          expectation: Expectation = Expectation()):
    CHECKER.check(put,
                  source,
                  model_constructor,
                  integration_check.arrangement_wo_tcds(arrangement),
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
                                     integration_check.arrangement_wo_tcds(arrangement),
                                     expectation,
                                     )
