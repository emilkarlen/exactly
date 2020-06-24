from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTrace
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class MatcherSdv(Generic[MODEL],
                 LogicSdv[MatcherWTrace[MODEL]],
                 ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        pass
