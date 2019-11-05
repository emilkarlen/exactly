from typing import Sequence, Callable

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
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


class LineMatcherResolverFromParts(LineMatcherResolver):
    def __init__(self,
                 references: Sequence[SymbolReference],
                 make_value: Callable[[SymbolTable], LineMatcherValue]):
        self._make_value = make_value
        self._references = references

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        return self._make_value(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self))


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
