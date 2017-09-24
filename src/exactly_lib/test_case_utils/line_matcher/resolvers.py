from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.resolver_structure import LineMatcherResolver
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.line_matcher import line_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class LineMatcherConstantResolver(LineMatcherResolver):
    """
    A :class:`LineMatcherResolver` that is a constant :class:`LineMatcher`
    """

    def __init__(self, value: LineMatcher):
        self._value = value

    def resolve(self, symbols: SymbolTable) -> LineMatcher:
        return self._value

    @property
    def references(self) -> list:
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

    def resolve(self, symbols: SymbolTable) -> LineMatcher:
        container = symbols.lookup(self._name_of_referenced_resolver)
        resolver = container.resolver
        assert isinstance(resolver, LineMatcherResolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> list:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''


class LineMatcherNotResolver(LineMatcherResolver):
    """
    Resolver of :class:`LineMatcherNot`
    """

    def __init__(self, line_matcher_resolver: LineMatcherResolver):
        self._resolver = line_matcher_resolver

    def resolve(self, symbols: SymbolTable) -> LineMatcher:
        return line_matchers.LineMatcherNot(self._resolver.resolve(symbols))

    @property
    def references(self) -> list:
        return self._resolver.references


class LineMatcherAndResolver(LineMatcherResolver):
    """
    Resolver of :class:`LineMatcherAnd`
    """

    def __init__(self, line_matcher_resolver_list: list):
        self._resolvers = line_matcher_resolver_list
        self._references = references_from_objects_with_symbol_references(line_matcher_resolver_list)

    def resolve(self, symbols: SymbolTable) -> LineMatcher:
        return line_matchers.LineMatcherAnd([
            resolver.resolve(symbols)
            for resolver in self._resolvers
        ])

    @property
    def references(self) -> list:
        return self._references


class LineMatcherOrResolver(LineMatcherResolver):
    """
    Resolver of :class:`LineMatcherOr`
    """

    def __init__(self, line_matcher_resolver_list: list):
        self._resolvers = line_matcher_resolver_list
        self._references = references_from_objects_with_symbol_references(line_matcher_resolver_list)

    def resolve(self, symbols: SymbolTable) -> LineMatcher:
        return line_matchers.LineMatcherOr([
            resolver.resolve(symbols)
            for resolver in self._resolvers
        ])

    @property
    def references(self) -> list:
        return self._references
