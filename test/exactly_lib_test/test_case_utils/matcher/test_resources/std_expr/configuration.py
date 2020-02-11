from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.matcher import MatcherSdv, MatcherTypeSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import MatcherChecker

MODEL = TypeVar('MODEL')


class MatcherConfiguration(Generic[MODEL], ABC):
    @abstractmethod
    def mk_logic_type(self, generic: MatcherSdv[MODEL]) -> MatcherTypeSdv[MODEL]:
        pass

    @abstractmethod
    def logic_type(self) -> LogicValueType:
        pass

    @abstractmethod
    def parser(self) -> Parser[MatcherTypeSdv[MODEL]]:
        pass

    @abstractmethod
    def checker(self) -> MatcherChecker[MODEL]:
        pass

    @abstractmethod
    def arbitrary_model(self, environment: FullResolvingEnvironment) -> MODEL:
        pass

    def valid_symbol_name_and_not_valid_primitive_or_operator(self) -> str:
        return 'VALID_SYMBOL_NAME_AND_NOT_VALID_PRIMITIVE_OR_OPERATOR'

    def not_a_valid_symbol_name_nor_valid_primitive_or_operator(self) -> str:
        return 'not/a/valid/symbol/name'
