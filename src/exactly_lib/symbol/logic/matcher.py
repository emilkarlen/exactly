from abc import ABC, abstractmethod
from typing import Generic

from exactly_lib.symbol.logic.logic_type_sdv import LogicWithStructureSdv, MODEL
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTraceAndNegation
from exactly_lib.util.symbol_table import SymbolTable


class MatcherSdv(Generic[MODEL],
                 LogicWithStructureSdv[MatcherWTraceAndNegation[MODEL]],
                 ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        pass
