from typing import Sequence

from exactly_lib.symbol.resolver_structure import StringTransformerResolver, LineMatcherResolver
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.string_transformer import transformers
from exactly_lib.type_system.logic import string_transformer_values
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerValue
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerConstant(StringTransformerResolver):
    """
    A :class:`LinesTransformerResolver` that is a constant :class:`LinesTransformer`
    """

    def __init__(self, value: StringTransformer):
        self._value = string_transformer_values.StringTransformerConstantValue(value)

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class StringTransformerConstantOfValue(StringTransformerResolver):
    """
    A :class:`LinesTransformerResolver` that is a constant :class:`LinesTransformerValue`
    """

    def __init__(self, value: StringTransformerValue):
        self._value = value

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class StringTransformerReference(StringTransformerResolver):
    """
    A :class:`LinesTransformerResolver` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_resolver: str):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [SymbolReference(name_of_referenced_resolver,
                                            ValueTypeRestriction(ValueType.STRING_TRANSFORMER))]

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        container = symbols.lookup(self._name_of_referenced_resolver)
        resolver = container.resolver
        assert isinstance(resolver, StringTransformerResolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''


class StringTransformerSelectResolver(StringTransformerResolver):
    """
    Resolver of :class:`SelectLinesTransformer`
    """

    def __init__(self, line_matcher_resolver: LineMatcherResolver):
        self.line_matcher_resolver = line_matcher_resolver

    def resolve(self, symbols: SymbolTable) -> StringTransformer:
        return string_transformer_values.StringTransformerConstantValue(
            transformers.SelectStringTransformer(self.line_matcher_resolver.resolve(symbols)))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.line_matcher_resolver.references
