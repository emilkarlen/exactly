from typing import Sequence

from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.resolver_structure import StringTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic import string_transformer_values
from exactly_lib.type_system.logic.string_transformer import StringTransformerValue
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerSequenceResolver(StringTransformerResolver):
    def __init__(self, transformer_resolver_list: Sequence[StringTransformerResolver]):
        self.transformers = transformer_resolver_list
        self._references = references_from_objects_with_symbol_references(transformer_resolver_list)

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        return string_transformer_values.StringTransformerSequenceValue([
            transformer.resolve(symbols)
            for transformer in self.transformers
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references
