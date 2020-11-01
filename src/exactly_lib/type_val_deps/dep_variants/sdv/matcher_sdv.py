from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_deps.dep_variants.ddv.matcher_ddv import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.logic_type_sdv import LogicSdv
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class MatcherSdv(Generic[MODEL],
                 LogicSdv[MatcherWTrace[MODEL]],
                 ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        pass
