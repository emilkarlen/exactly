from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.named_element.resolver_structure import FileMatcherResolver
from exactly_lib.named_element.restriction import ValueTypeRestriction
from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherFromSelectors
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util import dir_contents_selection as dcs
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
        self._references = [NamedElementReference(name_of_referenced_resolver,
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


class FileMatcherAndResolver(FileMatcherResolver):
    """
    A :class:`FileMatcherResolver` that combines selectors using AND.
    """

    def __init__(self, resolvers: list):
        self._resolvers = tuple(resolvers)
        self._references = references_from_objects_with_symbol_references(resolvers)

    def resolve(self, symbols: SymbolTable) -> FileMatcher:
        selectors = dcs.and_all([resolver.resolve(symbols).selectors for resolver in self._resolvers])
        return FileMatcherFromSelectors(selectors)

    @property
    def references(self) -> list:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + 'num resolvers = ' + str(len(self._resolvers)) + '\''
