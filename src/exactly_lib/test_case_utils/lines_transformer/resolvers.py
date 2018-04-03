from typing import Sequence

from exactly_lib.symbol.resolver_structure import LinesTransformerResolver, LineMatcherResolver
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.lines_transformer import transformers
from exactly_lib.type_system.logic import lines_transformer_values
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer, LinesTransformerValue
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class LinesTransformerConstant(LinesTransformerResolver):
    """
    A :class:`LinesTransformerResolver` that is a constant :class:`LinesTransformer`
    """

    def __init__(self, value: LinesTransformer):
        self._value = lines_transformer_values.LinesTransformerConstantValue(value)

    def resolve(self, symbols: SymbolTable) -> LinesTransformerValue:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class LinesTransformerConstantOfValue(LinesTransformerResolver):
    """
    A :class:`LinesTransformerResolver` that is a constant :class:`LinesTransformerValue`
    """

    def __init__(self, value: LinesTransformerValue):
        self._value = value

    def resolve(self, symbols: SymbolTable) -> LinesTransformerValue:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class LinesTransformerReference(LinesTransformerResolver):
    """
    A :class:`LinesTransformerResolver` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_resolver: str):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [SymbolReference(name_of_referenced_resolver,
                                            ValueTypeRestriction(ValueType.LINES_TRANSFORMER))]

    def resolve(self, symbols: SymbolTable) -> LinesTransformerValue:
        container = symbols.lookup(self._name_of_referenced_resolver)
        resolver = container.resolver
        assert isinstance(resolver, LinesTransformerResolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''


class LinesTransformerSelectResolver(LinesTransformerResolver):
    """
    Resolver of :class:`SelectLinesTransformer`
    """

    def __init__(self, line_matcher_resolver: LineMatcherResolver):
        self.line_matcher_resolver = line_matcher_resolver

    def resolve(self, symbols: SymbolTable) -> LinesTransformer:
        return lines_transformer_values.LinesTransformerConstantValue(
            transformers.SelectLinesTransformer(self.line_matcher_resolver.resolve(symbols)))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.line_matcher_resolver.references
