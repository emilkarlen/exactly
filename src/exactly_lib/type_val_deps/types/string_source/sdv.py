from abc import ABC, abstractmethod

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsWithNodeDescriptionSdv
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.symbol_table import SymbolTable


class StringSourceSdv(FullDepsWithNodeDescriptionSdv[StringSource], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> StringSourceDdv:
        pass
