from abc import ABC, abstractmethod

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsWithDetailsDescriptionSdv
from exactly_lib.type_val_deps.types.files_condition.ddv import FilesConditionDdv
from exactly_lib.type_val_prims.files_condition import FilesCondition
from exactly_lib.util.symbol_table import SymbolTable


class FilesConditionSdv(FullDepsWithDetailsDescriptionSdv[FilesCondition], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FilesConditionDdv:
        pass
