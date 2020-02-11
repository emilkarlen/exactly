from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.symbol.sdv_structure import SymbolDependentTypeValue, SymbolDependentValue
from exactly_lib.type_system.logic.logic_base_class import LogicDdv, LogicWithStructureDdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTraceAndNegation
from exactly_lib.type_system.value_type import TypeCategory, LogicValueType
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')
MODEL = TypeVar('MODEL')


class LogicSdv(Generic[PRIMITIVE], SymbolDependentValue, ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> LogicDdv[PRIMITIVE]:
        pass


class LogicWithStructureSdv(Generic[PRIMITIVE], LogicSdv[PRIMITIVE], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> LogicWithStructureDdv[PRIMITIVE]:
        pass


class LogicTypeSdv(Generic[PRIMITIVE],
                   LogicWithStructureSdv[PRIMITIVE],
                   SymbolDependentTypeValue,
                   ABC):
    """ Base class for logic values - values that represent functionality/logic."""

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.LOGIC

    @property
    def logic_value_type(self) -> LogicValueType:
        raise NotImplementedError('abstract method')


def get_logic_value_type(sdv: LogicTypeSdv) -> LogicValueType:
    return sdv.logic_value_type


class MatcherTypeSdv(Generic[MODEL],
                     LogicTypeSdv[MatcherWTraceAndNegation[MODEL]],
                     ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        pass
