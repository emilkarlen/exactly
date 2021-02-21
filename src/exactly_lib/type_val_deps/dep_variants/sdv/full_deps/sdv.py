from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsDdv, FullDepsWithDetailsDescriptionDdv, \
    FullDepsWithNodeDescriptionDdv
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')


class FullDepsSdv(Generic[PRIMITIVE], SymbolDependentValue, ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FullDepsDdv[PRIMITIVE]:
        pass

    @staticmethod
    def resolve__optional(sdv: Optional['FullDepsSdv[PRIMITIVE]'],
                          symbols: SymbolTable,
                          ) -> Optional[FullDepsDdv[PRIMITIVE]]:
        return (
            None
            if sdv is None
            else
            sdv.resolve(symbols)
        )


class FullDepsWithDetailsDescriptionSdv(Generic[PRIMITIVE], FullDepsSdv[PRIMITIVE], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FullDepsWithDetailsDescriptionDdv[PRIMITIVE]:
        pass


class FullDepsWithNodeDescriptionSdv(Generic[PRIMITIVE], FullDepsSdv[PRIMITIVE], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FullDepsWithNodeDescriptionDdv[PRIMITIVE]:
        pass
