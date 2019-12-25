from abc import ABC, abstractmethod
from typing import Sequence, Generic

from exactly_lib.symbol.logic.matcher import MODEL
from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.type_system.value_type import TypeCategory, LogicValueType
from exactly_lib.util.symbol_table import SymbolTable


class LogicTypeSdv(SymbolDependentValue, ABC):
    """ Base class for logic values - values that represent functionality/logic."""

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.LOGIC

    @property
    def logic_value_type(self) -> LogicValueType:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> WithTreeStructureDescription:
        raise NotImplementedError('abstract method')


def get_logic_value_type(sdv: LogicTypeSdv) -> LogicValueType:
    return sdv.logic_value_type


class MatcherTypeSdv(Generic[MODEL], LogicTypeSdv, ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        pass
