from typing import Sequence, List

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.line_matcher import line_matcher_values as values
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherValue
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class LineMatcherConstantResolver(LineMatcherResolver):
    def __init__(self, value: LineMatcher):
        self._value = values.LineMatcherValueFromPrimitiveValue(value)

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class LineMatcherReferenceResolver(LineMatcherResolver):
    """
    A :class:`LineMatcherResolver` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_resolver: str):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [SymbolReference(name_of_referenced_resolver,
                                            ValueTypeRestriction(ValueType.LINE_MATCHER))]

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        resolver = lookups.lookup_line_matcher(symbols, self._name_of_referenced_resolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''


class LineMatcherNotResolver(LineMatcherResolver):
    def __init__(self, line_matcher_resolver: LineMatcherResolver):
        self._resolver = line_matcher_resolver

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        return values.LineMatcherNotValue(self._resolver.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._resolver.references


class LineMatcherAndResolver(LineMatcherResolver):
    def __init__(self, parts: List[LineMatcherResolver]):
        self._parts = parts
        self._references = references_from_objects_with_symbol_references(parts)

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        return values.LineMatcherAndValue([
            part.resolve(symbols)
            for part in self._parts
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class LineMatcherOrResolver(LineMatcherResolver):
    def __init__(self, parts: List[LineMatcherResolver]):
        self._parts = parts
        self._references = references_from_objects_with_symbol_references(parts)

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        return values.LineMatcherOrValue([
            part.resolve(symbols)
            for part in self._parts
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references
