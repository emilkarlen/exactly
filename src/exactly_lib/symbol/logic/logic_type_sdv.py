from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence

from exactly_lib.symbol.sdv_structure import SymbolDependentTypeValue, SymbolDependentValue, SymbolReference
from exactly_lib.type_system.logic.logic_base_class import LogicDdv, LogicWithStructureDdv
from exactly_lib.type_system.value_type import TypeCategory, LogicValueType
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')


class LogicSdv(Generic[PRIMITIVE], SymbolDependentValue, ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> LogicDdv[PRIMITIVE]:
        pass


class LogicWithStructureSdv(Generic[PRIMITIVE], LogicSdv[PRIMITIVE], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> LogicWithStructureDdv[PRIMITIVE]:
        pass


class LogicTypeStv(Generic[PRIMITIVE],
                   SymbolDependentTypeValue,
                   ABC):
    """ Base class for logic Values in the Symbol Table - values that represent functionality/logic."""

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.LOGIC

    @property
    @abstractmethod
    def logic_value_type(self) -> LogicValueType:
        pass

    @abstractmethod
    def value(self) -> LogicSdv[PRIMITIVE]:
        pass

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.value().references

    def resolve(self, symbols: SymbolTable) -> LogicDdv[PRIMITIVE]:
        return self.value().resolve(symbols)


def get_logic_value_type(sdv: LogicTypeStv) -> LogicValueType:
    return sdv.logic_value_type
