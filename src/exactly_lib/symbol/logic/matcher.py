from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.symbol.logic.logic_type_sdv import LogicWithStructureSdv, LogicTypeSdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTraceAndNegation
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class MatcherSdv(Generic[MODEL],
                 LogicWithStructureSdv[MatcherWTraceAndNegation[MODEL]],
                 ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        pass


class MatcherTypeSdv(Generic[MODEL],
                     LogicTypeSdv[MatcherWTraceAndNegation[MODEL]],
                     ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        pass
