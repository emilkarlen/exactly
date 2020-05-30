from abc import ABC, abstractmethod

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerSdv(LogicSdv[StringTransformer], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        pass
