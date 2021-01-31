from typing import Sequence

from exactly_lib.definitions.entity import types
from exactly_lib.impls.types.expression.descriptions.operator import InfixOperatorDescriptionFromFunctions
from exactly_lib.impls.types.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.impls.types.string_transformer.impl.sequence import StringTransformerSequenceDdv
from exactly_lib.symbol.sdv_structure import references_from_objects_with_symbol_references, SymbolReference
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.ddvs import StringTransformerConstantDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.textformat_parser import TextParser


class StringTransformerSequenceSdv(StringTransformerSdv):
    def __init__(self, transformers: Sequence[StringTransformerSdv]):
        self.transformers = transformers
        self._references = references_from_objects_with_symbol_references(transformers)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        num_transformers = len(self.transformers)
        if num_transformers == 0:
            return StringTransformerConstantDdv(IdentityStringTransformer())
        elif num_transformers == 1:
            return self.transformers[0].resolve(symbols)
        else:
            return StringTransformerSequenceDdv([
                transformer.resolve(symbols)
                for transformer in self.transformers
            ])


_SEQUENCE_TRANSFORMER_SED_DESCRIPTION = """\
Composition of {_TRANSFORMER_:s}.


The output of the {_TRANSFORMER_} to the left is given as input to
the {_TRANSFORMER_} to the right.
"""

_TEXT_PARSER = TextParser({
    '_TRANSFORMER_': types.STRING_TRANSFORMER_TYPE_INFO.name,

})

SYNTAX_DESCRIPTION = InfixOperatorDescriptionFromFunctions(
    _TEXT_PARSER.fnap__fun(_SEQUENCE_TRANSFORMER_SED_DESCRIPTION)
)
