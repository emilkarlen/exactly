from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.type_system.logic.logic_base_class import LogicDdv
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')


class LogicSdv(Generic[PRIMITIVE], SymbolDependentValue, ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> LogicDdv[PRIMITIVE]:
        pass
