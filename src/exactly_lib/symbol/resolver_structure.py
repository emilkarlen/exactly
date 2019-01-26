from typing import Sequence, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.object_with_symbol_references import ObjectWithSymbolReferences
from exactly_lib.type_system.value_type import ValueType, TypeCategory
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.symbol_table import SymbolTableValue, SymbolTable


class SymbolValueResolver(ObjectWithSymbolReferences):
    """ Base class for values in the symbol table used by Exactly. """

    @property
    def type_category(self) -> TypeCategory:
        raise NotImplementedError('abstract method')

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> Sequence:
        """
        All :class:`SymbolReference` directly referenced by this object.

        :type: [`SymbolReference`]
        """
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable):
        raise NotImplementedError('abstract method')


def get_references(resolver: SymbolValueResolver) -> Sequence:
    return resolver.references


def get_type_category(resolver: SymbolValueResolver) -> TypeCategory:
    return resolver.type_category


def get_value_type(resolver: SymbolValueResolver) -> ValueType:
    return resolver.value_type


class SymbolContainer(SymbolTableValue):
    """
    The info about a symbol resolver that is stored in a symbol table.

    A value together with meta info
    """

    def __init__(self,
                 value_resolver: SymbolValueResolver,
                 source_location: Optional[SourceLocationInfo]):
        self._resolver = value_resolver
        self._source_location = source_location

    @property
    def source_location(self) -> Optional[SourceLocationInfo]:
        return self._source_location

    @property
    def definition_source(self) -> LineSequence:
        """
        The source code of the definition of the value.

        :rtype None iff the symbol is built in.
        """
        return None \
            if self._source_location is None else \
            self._source_location.source_location_path.location.source

    @property
    def resolver(self) -> SymbolValueResolver:
        return self._resolver


def container_of_builtin(value_resolver: SymbolValueResolver) -> SymbolContainer:
    return SymbolContainer(value_resolver, None)
