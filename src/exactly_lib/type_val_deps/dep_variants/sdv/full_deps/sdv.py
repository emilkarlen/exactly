from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.symbol.sdv_structure import TypedSymbolDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsDdv, FullDepsWithDetailsDescriptionDdv, \
    FullDepsWithNodeDescriptionDdv
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')


class FullDepsSdv(Generic[PRIMITIVE], TypedSymbolDependentValue[FullDepsDdv[PRIMITIVE]], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FullDepsDdv[PRIMITIVE]:
        raise NotImplementedError('abstract method')


class FullDepsWithDetailsDescriptionSdv(Generic[PRIMITIVE], FullDepsSdv[PRIMITIVE], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FullDepsWithDetailsDescriptionDdv[PRIMITIVE]:
        raise NotImplementedError('abstract method')


class FullDepsWithNodeDescriptionSdv(Generic[PRIMITIVE], FullDepsSdv[PRIMITIVE], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FullDepsWithNodeDescriptionDdv[PRIMITIVE]:
        raise NotImplementedError('abstract method')
