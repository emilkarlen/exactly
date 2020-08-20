from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.expression.parser import GrammarParsers
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.symbol.test_resources.symbols_setup import MatcherSymbolValueContext, MatcherTypeSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

MODEL = TypeVar('MODEL')

MatcherCheckerAlias = IntegrationChecker[MatcherWTrace[MODEL],
                                         Callable[[FullResolvingEnvironment], MODEL],
                                         ValueAssertion[MatchingResult]]


class MatcherConfiguration(Generic[MODEL], ABC):
    @abstractmethod
    def mk_logic_type_value_context_of_primitive(self,
                                                 primitive: MatcherWTrace[MODEL]
                                                 ) -> MatcherSymbolValueContext[MODEL]:
        pass

    @abstractmethod
    def mk_logic_type_context_of_primitive(self,
                                           name: str,
                                           primitive: MatcherWTrace[MODEL]
                                           ) -> MatcherTypeSymbolContext[MODEL]:
        pass

    @abstractmethod
    def mk_logic_type_context_of_sdv(self,
                                     name: str,
                                     sdv: MatcherSdv[MODEL]
                                     ) -> MatcherTypeSymbolContext[MODEL]:
        pass

    @abstractmethod
    def logic_type(self) -> LogicValueType:
        pass

    @abstractmethod
    def parsers_for_expr_on_any_line(self) -> GrammarParsers[MatcherSdv[MODEL]]:
        pass

    @abstractmethod
    def checker_for_parser_of_full_expr(self) -> IntegrationChecker[MatcherWTrace[MODEL],
                                                                    Callable[[FullResolvingEnvironment], MODEL],
                                                                    MatchingResult]:
        pass

    @abstractmethod
    def arbitrary_model(self, environment: FullResolvingEnvironment) -> MODEL:
        pass

    def valid_symbol_name_and_not_valid_primitive_or_operator(self) -> str:
        return 'VALID_SYMBOL_NAME_AND_NOT_VALID_PRIMITIVE_OR_OPERATOR'

    def not_a_valid_symbol_name_nor_valid_primitive_or_operator(self) -> str:
        return 'not/a/valid/symbol/name'
