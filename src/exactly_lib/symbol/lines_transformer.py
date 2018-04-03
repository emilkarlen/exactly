from typing import Sequence

from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic import lines_transformer_values
from exactly_lib.type_system.logic.lines_transformer import LinesTransformerValue
from exactly_lib.util.symbol_table import SymbolTable


class LinesTransformerSequenceResolver(LinesTransformerResolver):
    def __init__(self, transformer_resolver_list: Sequence[LinesTransformerResolver]):
        self.transformers = transformer_resolver_list
        self._references = references_from_objects_with_symbol_references(transformer_resolver_list)

    def resolve(self, symbols: SymbolTable) -> LinesTransformerValue:
        return lines_transformer_values.LinesTransformerSequenceValue([
            transformer.resolve(symbols)
            for transformer in self.transformers
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references