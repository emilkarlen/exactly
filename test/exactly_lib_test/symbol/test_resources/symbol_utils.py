from exactly_lib.symbol import resolver_structure
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import AnySymbolTypeRestriction
from exactly_lib.symbol.data.string_resolver import string_constant
from exactly_lib.symbol.data.value_restriction import ValueRestriction
from exactly_lib.symbol.resolver_structure import SymbolContainer, DataValueResolver, \
    SymbolValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable, Entry


def container(value_resolver: SymbolValueResolver,
              line_num: int = 1,
              source_line: str = 'value def line') -> SymbolContainer:
    return SymbolContainer(value_resolver, Line(line_num, source_line))


def container_of_builtin(value_resolver: SymbolValueResolver) -> SymbolContainer:
    return resolver_structure.container_of_builtin(value_resolver)


def element_reference(name: str,
                      value_restriction: ValueRestriction = AnySymbolTypeRestriction()) -> SymbolReference:
    return SymbolReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))


def entry_with_arbitrary_element(name: str,
                                 value_resolver: DataValueResolver = string_constant('string value'),
                                 line_num: int = 1,
                                 source_line: str = 'value def line') -> Entry:
    return Entry(name, SymbolContainer(value_resolver,
                                       Line(line_num, source_line)))


def symbol_table_from_symbol_definitions(definitions: iter) -> SymbolTable:
    """
    :param definitions: [`NamedElementDefinition`]
    """
    elements = [(ned.name, ned.resolver_container)
                for ned in definitions]
    return SymbolTable(dict(elements))
