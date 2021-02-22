from typing import Sequence, Callable

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref import symbol_lookup
from exactly_lib.type_val_deps.sym_ref.restrictions import ValueTypeRestriction
from exactly_lib.type_val_deps.types.string_transformer import ddvs
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerSdvConstant(StringTransformerSdv):
    """
    A :class:`LinesTransformerSdv` that is a constant :class:`LinesTransformer`
    """

    def __init__(self, value: StringTransformer):
        self._value = ddvs.StringTransformerConstantDdv(value)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return self._value

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class SdvFromParts(StringTransformerSdv):
    def __init__(self,
                 make_ddv: Callable[[SymbolTable], StringTransformerDdv],
                 symbol_references: Sequence[SymbolReference] = (),
                 ):
        self._make_ddv = make_ddv
        self._symbol_references = symbol_references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._symbol_references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return self._make_ddv(symbols)


class StringTransformerSdvConstantOfDdv(StringTransformerSdv):
    """
    A :class:`StringTransformerSdv` that is a constant :class:`StringTransformerDdv`
    """

    def __init__(self, ddv: StringTransformerDdv):
        self._ddv = ddv

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return self._ddv

    def __str__(self):
        return str(type(self)) + '\'' + str(self._ddv) + '\''


class StringTransformerSdvReference(StringTransformerSdv):
    """
    A :class:`StringTransformerSdv` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_sdv: str):
        self._name_of_referenced_sdv = name_of_referenced_sdv
        self._references = [SymbolReference(name_of_referenced_sdv,
                                            ValueTypeRestriction.of_single(ValueType.STRING_TRANSFORMER))]

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        sdv = symbol_lookup.lookup_string_transformer(symbols, self._name_of_referenced_sdv)
        return sdv.resolve(symbols)

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_sdv) + '\''
