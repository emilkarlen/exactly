from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FileMatcherConstantResolver(FileMatcherResolver):
    """
    A :class:`FileMatcherResolver` that is a constant :class:`FileMatcher`
    """

    def __init__(self, value: FileMatcher):
        self._value = value

    def resolve(self, symbols: SymbolTable) -> FileMatcher:
        return self._value

    @property
    def references(self) -> list:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class FileMatcherReferenceResolver(FileMatcherResolver):
    """
    A :class:`FileMatcherResolver` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_resolver: str):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [SymbolReference(name_of_referenced_resolver,
                                            ValueTypeRestriction(ValueType.FILE_MATCHER))]

    def resolve(self, symbols: SymbolTable) -> FileMatcher:
        container = symbols.lookup(self._name_of_referenced_resolver)
        resolver = container.resolver
        assert isinstance(resolver, FileMatcherResolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> list:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''


class FileMatcherNotResolver(FileMatcherResolver):
    """
    Resolver of :class:`FileMatcherNot`
    """

    def __init__(self, file_matcher_resolver: FileMatcherResolver):
        self._resolver = file_matcher_resolver

    def resolve(self, symbols: SymbolTable) -> FileMatcher:
        return file_matchers.FileMatcherNot(self._resolver.resolve(symbols))

    @property
    def references(self) -> list:
        return self._resolver.references


class FileMatcherAndResolver(FileMatcherResolver):
    """
    Resolver of :class:`FileMatcherAnd`
    """

    def __init__(self, file_matcher_resolver_list: list):
        self._resolvers = file_matcher_resolver_list
        self._references = references_from_objects_with_symbol_references(file_matcher_resolver_list)

    def resolve(self, symbols: SymbolTable) -> FileMatcher:
        return file_matchers.FileMatcherAnd([
            resolver.resolve(symbols)
            for resolver in self._resolvers
        ])

    @property
    def references(self) -> list:
        return self._references


class FileMatcherOrResolver(FileMatcherResolver):
    """
    Resolver of :class:`FileMatcherOr`
    """

    def __init__(self, file_matcher_resolver_list: list):
        self._resolvers = file_matcher_resolver_list
        self._references = references_from_objects_with_symbol_references(file_matcher_resolver_list)

    def resolve(self, symbols: SymbolTable) -> FileMatcher:
        return file_matchers.FileMatcherOr([
            resolver.resolve(symbols)
            for resolver in self._resolvers
        ])

    @property
    def references(self) -> list:
        return self._references
