from typing import Sequence

from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic import string_transformer_ddvs
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerSequenceSdv(StringTransformerSdv):
    def __init__(self, transformers: Sequence[StringTransformerSdv]):
        self.transformers = transformers
        self._references = references_from_objects_with_symbol_references(transformers)

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return string_transformer_ddvs.StringTransformerSequenceDdv([
            transformer.resolve(symbols)
            for transformer in self.transformers
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references
