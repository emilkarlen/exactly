from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.matcher_base_class import MatcherValue
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class MatcherResolver(Generic[T], ABC):
    @property
    @abstractmethod
    def references(self) -> Sequence[SymbolReference]:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> MatcherValue[T]:
        pass
