from typing import TypeVar, Generic

from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.util.symbol_table import SymbolTable

RESOLVED_TYPE = TypeVar('RESOLVED_TYPE')


class ValueResolver(Generic[RESOLVED_TYPE], ObjectWithTypedSymbolReferences):
    def resolve_value(self, symbols: SymbolTable) -> RESOLVED_TYPE:
        raise NotImplementedError('abstract method')
