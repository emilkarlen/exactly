from exactly_lib.named_element import resolver_structure
from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.resolver_structure import NamedElementContainer, SymbolValueResolver, \
    NamedElementResolver
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.named_element.symbol.restrictions.value_restrictions import NoRestriction
from exactly_lib.named_element.symbol.string_resolver import string_constant
from exactly_lib.named_element.symbol.value_restriction import ValueRestriction
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable, Entry


def container(value_resolver: NamedElementResolver,
              line_num: int = 1,
              source_line: str = 'value def line') -> NamedElementContainer:
    return NamedElementContainer(value_resolver, Line(line_num, source_line))


def container_of_builtin(value_resolver: NamedElementResolver) -> NamedElementContainer:
    return resolver_structure.container_of_builtin(value_resolver)


def element_reference(name: str, value_restriction: ValueRestriction = NoRestriction()) -> NamedElementReference:
    return NamedElementReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))


def entry_with_arbitrary_element(name: str,
                                 value_resolver: SymbolValueResolver = string_constant('string value'),
                                 line_num: int = 1,
                                 source_line: str = 'value def line') -> Entry:
    return Entry(name, NamedElementContainer(value_resolver,
                                             Line(line_num, source_line)))


def symbol_table_from_symbol_definitions(definitions: iter) -> SymbolTable:
    """
    :param definitions: [`NamedElementDefinition`]
    """
    elements = [(ned.name, ned.resolver_container)
                for ned in definitions]
    return SymbolTable(dict(elements))
