from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence

from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class MatcherSdv(Generic[MODEL], ObjectWithTypedSymbolReferences, ABC):
    @property
    @abstractmethod
    def references(self) -> Sequence[SymbolReference]:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        pass
