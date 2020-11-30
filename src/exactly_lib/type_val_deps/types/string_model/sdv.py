from abc import ABC, abstractmethod

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsWithNodeDescriptionSdv
from exactly_lib.type_val_deps.types.string_model.ddv import StringModelDdv
from exactly_lib.type_val_prims.string_model.string_model import StringModel
from exactly_lib.util.symbol_table import SymbolTable


class StringModelSdv(FullDepsWithNodeDescriptionSdv[StringModel], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> StringModelDdv:
        pass
