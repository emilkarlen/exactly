import pathlib
from typing import Sequence

from exactly_lib.section_document.source_location import FileLocationInfo, SourceLocationInfo
from exactly_lib.symbol import resolver_structure
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.data_value_resolver import DataValueResolver
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction
from exactly_lib.symbol.data.value_restriction import ValueRestriction
from exactly_lib.symbol.resolver_structure import SymbolContainer, SymbolValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference, SymbolDefinition
from exactly_lib.util import line_source
from exactly_lib.util.symbol_table import SymbolTable, Entry


def container(value_resolver: SymbolValueResolver,
              line_num: int = 1,
              source_line: str = 'value def line') -> SymbolContainer:
    return SymbolContainer(value_resolver,
                           single_line_sequence(line_num, source_line))


def container_of_builtin(value_resolver: SymbolValueResolver) -> SymbolContainer:
    return resolver_structure.container_of_builtin(value_resolver)


def element_reference(name: str,
                      value_restriction: ValueRestriction = AnyDataTypeRestriction()) -> SymbolReference:
    return SymbolReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))


def entry_with_arbitrary_element(name: str,
                                 value_resolver: DataValueResolver = string_resolvers.str_constant('string value'),
                                 line_num: int = 1,
                                 source_line: str = 'value def line') -> Entry:
    return Entry(name, SymbolContainer(value_resolver,
                                       single_line_sequence(line_num, source_line)))


def definition_with_arbitrary_element(name: str,
                                      value_resolver: DataValueResolver = string_resolvers.str_constant('string value'),
                                      line_num: int = 1,
                                      source_line: str = 'value def line') -> SymbolDefinition:
    return SymbolDefinition(name, SymbolContainer(value_resolver,
                                                  single_line_sequence(line_num, source_line)))


def symbol_table_from_symbol_definitions(definitions: Sequence[SymbolDefinition]) -> SymbolTable:
    elements = [(sym_def.name, sym_def.resolver_container)
                for sym_def in definitions]
    return SymbolTable(dict(elements))


_FL = FileLocationInfo(pathlib.Path('/'))


def single_line_sequence(line_number: int, line: str) -> SourceLocationInfo:
    return source_info_for_line_sequence(line_source.single_line_sequence(line_number, line))


def source_info_for_line_sequence(source: line_source.LineSequence) -> SourceLocationInfo:
    return _FL.source_location_info_for(source)
