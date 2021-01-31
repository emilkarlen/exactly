from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable

from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.symbol.value_type import LogicValueType
from exactly_lib.type_val_deps.dep_variants.sdv.matcher import MatcherSdv
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.logic.test_resources.matcher_symbol_context import MatcherSymbolValueContext, \
    MatcherTypeSymbolContext

MODEL = TypeVar('MODEL')

MatcherCheckerAlias = IntegrationChecker[MatcherWTrace[MODEL],
                                         Callable[[FullResolvingEnvironment], MODEL],
                                         Assertion[MatchingResult]]


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
