from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsWithNodeDescriptionSdv
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class MatcherSdv(Generic[MODEL],
                 FullDepsWithNodeDescriptionSdv[MatcherWTrace[MODEL]],
                 ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        pass
