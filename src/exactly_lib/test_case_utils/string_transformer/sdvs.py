from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.logic import string_transformer_ddvs
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerSdvConstant(StringTransformerSdv):
    """
    A :class:`LinesTransformerSdv` that is a constant :class:`LinesTransformer`
    """

    def __init__(self, value: StringTransformer):
        self._value = string_transformer_ddvs.StringTransformerConstantDdv(value)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return self._value

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


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
                                            ValueTypeRestriction(ValueType.STRING_TRANSFORMER))]

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        sdv = lookups.lookup_string_transformer(symbols, self._name_of_referenced_sdv)
        return sdv.resolve(symbols)

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_sdv) + '\''
