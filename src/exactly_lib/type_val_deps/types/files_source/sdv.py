from abc import ABC, abstractmethod

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsWithNodeDescriptionSdv
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib.util.symbol_table import SymbolTable
from .ddv import FilesSourceDdv


class FilesSourceSdv(FullDepsWithNodeDescriptionSdv[FilesSource], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FilesSourceDdv:
        pass
