import itertools

from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.resolver_structure import FileSelectorResolver
from exactly_lib.named_element.restriction import ElementTypeRestriction
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.type_system_values.value_type import ElementType
from exactly_lib.util import dir_contents_selection as dcs
from exactly_lib.util.symbol_table import SymbolTable


class FileSelectorConstant(FileSelectorResolver):
    """
    A :class:`FileSelectorResolver` that is a constant :class:`FileSelector`
    """

    def __init__(self, value: FileSelector):
        self._value = value

    def resolve(self, symbols: SymbolTable) -> FileSelector:
        return self._value

    @property
    def references(self) -> list:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class FileSelectorReference(FileSelectorResolver):
    """
    A :class:`FileSelectorResolver` that is a constant :class:`FileSelector`
    """

    def __init__(self, name_of_referenced_resolver: str):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [NamedElementReference(name_of_referenced_resolver,
                                                  ElementTypeRestriction(ElementType.FILE_SELECTOR))]

    def resolve(self, symbols: SymbolTable) -> FileSelector:
        container = symbols.lookup(self._name_of_referenced_resolver)
        resolver = container.resolver
        assert isinstance(resolver, FileSelectorResolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> list:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''


class FileSelectorAnd(FileSelectorResolver):
    """
    A :class:`FileSelectorResolver` that combines selectors using AND.
    """

    def __init__(self, resolvers: list):
        self._resolvers = tuple(resolvers)
        self._references = list(itertools.chain.from_iterable([r.references for r in resolvers]))

    def resolve(self, symbols: SymbolTable) -> FileSelector:
        selectors = dcs.and_all([resolver.resolve(symbols).selectors for resolver in self._resolvers])
        return FileSelector(selectors)

    @property
    def references(self) -> list:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + 'num resolvers = ' + str(len(self._resolvers)) + '\''
