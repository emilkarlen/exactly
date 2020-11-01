from abc import ABC, abstractmethod

from exactly_lib.type_val_deps.dep_variants.sdv.logic_type_sdv import LogicSdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerSdv(LogicSdv[StringTransformer], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        pass
