from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic import string_transformer_ddvs
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerConstant(StringTransformerResolver):
    """
    A :class:`LinesTransformerResolver` that is a constant :class:`LinesTransformer`
    """

    def __init__(self, value: StringTransformer):
        self._value = string_transformer_ddvs.StringTransformerConstantDdv(value)

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class StringTransformerConstantOfDdv(StringTransformerResolver):
    """
    A :class:`StringTransformerResolver` that is a constant :class:`StringTransformerValue`
    """

    def __init__(self, ddv: StringTransformerDdv):
        self._ddv = ddv

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return self._ddv

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._ddv) + '\''


class StringTransformerReference(StringTransformerResolver):
    """
    A :class:`StringTransformerResolver` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_resolver: str):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [SymbolReference(name_of_referenced_resolver,
                                            ValueTypeRestriction(ValueType.STRING_TRANSFORMER))]

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        resolver = lookups.lookup_string_transformer(symbols, self._name_of_referenced_resolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''
