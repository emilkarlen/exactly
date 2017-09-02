from exactly_lib.named_element import resolver_structure
from exactly_lib.named_element.named_element_usage import NamedElementDefinition, NamedElementReference
from exactly_lib.named_element.resolver_structure import NamedElementContainer, SymbolValueResolver
from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.named_element.symbol.restrictions.value_restrictions import AnySymbolTypeRestriction
from exactly_lib.named_element.symbol.string_resolver import string_constant
from exactly_lib.named_element.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.named_element.symbol.value_restriction import ValueRestriction
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.data import file_ref as _file_ref
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.list_value import ListValue
from exactly_lib.type_system.value_type import SymbolValueType
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib_test.named_element.symbol.test_resources.list_values import ListResolverTestImplForConstantListValue
from exactly_lib_test.named_element.symbol.test_resources.value_resolvers import ConstantValueResolver
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl


def container(value_resolver: SymbolValueResolver,
              line_num: int = 1,
              source_line: str = 'value def line') -> NamedElementContainer:
    return NamedElementContainer(value_resolver, Line(line_num, source_line))


def container_of_builtin(value_resolver: SymbolValueResolver) -> NamedElementContainer:
    return resolver_structure.container_of_builtin(value_resolver)


def string_constant_container(constant_str: str,
                              line_num: int = 1,
                              source_line: str = 'value def line') -> NamedElementContainer:
    return NamedElementContainer(string_constant(constant_str),
                                 Line(line_num, source_line))


def string_value_constant_container2(string_value: StringValue,
                                     line_num: int = 1,
                                     source_line: str = 'value def line') -> NamedElementContainer:
    return NamedElementContainer(ConstantValueResolver(SymbolValueType.STRING,
                                                       string_value),
                                 Line(line_num, source_line))


def string_symbol_definition(name: str, constant_str: str = 'string value') -> NamedElementDefinition:
    return NamedElementDefinition(name,
                                  string_constant_container(constant_str))


def string_value_symbol_definition(name: str, string_value: StringValue) -> NamedElementDefinition:
    return NamedElementDefinition(name,
                                  string_value_constant_container2(string_value))


def symbol_table_with_single_string_value(name: str, string_value: str = 'string value') -> SymbolTable:
    return symbol_table_from_symbol_definitions([string_symbol_definition(name, string_value)])


def symbol_table_with_string_values(name_and_value_pairs: iter) -> SymbolTable:
    sym_defs = [string_symbol_definition(name, value)
                for (name, value) in name_and_value_pairs]
    return symbol_table_from_symbol_definitions(sym_defs)


def symbol_table_with_string_values_from_name_and_value(name_and_value_list: iter) -> SymbolTable:
    """
    :type name_and_value_list: iter of NameAndValue
    """
    elements = [(name_and_value.name,
                 string_constant_container(name_and_value.value))
                for name_and_value in name_and_value_list]
    return SymbolTable(dict(elements))


def list_value_constant_container(list_value: ListValue,
                                  line_num: int = 1,
                                  source_line: str = 'value def line') -> NamedElementContainer:
    return NamedElementContainer(ListResolverTestImplForConstantListValue(list_value),
                                 Line(line_num, source_line))


def list_symbol_definition(name: str, resolved_value: ListValue) -> NamedElementDefinition:
    return NamedElementDefinition(name, list_value_constant_container(resolved_value))


def symbol_table_with_single_list_value(symbol_name: str, resolved_value: ListValue) -> SymbolTable:
    return symbol_table_from_symbol_definitions([list_symbol_definition(symbol_name, resolved_value)])


def file_ref_constant_container(
        file_ref_value: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                               relativity=RelOptionType.REL_CWD),
        line_num: int = 1,
        source_line: str = 'value def line') -> NamedElementContainer:
    return NamedElementContainer(FileRefConstant(file_ref_value),
                                 Line(line_num, source_line))


def file_ref_resolver_container(file_ref_resolver: FileRefResolver,
                                line_num: int = 1,
                                source_line: str = 'value def line') -> NamedElementContainer:
    return NamedElementContainer(file_ref_resolver,
                                 Line(line_num, source_line))


def file_ref_symbol_definition(
        name: str,
        file_ref_value: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                               relativity=RelOptionType.REL_CWD),
        line_num: int = 1,
        source_line: str = 'value def line'
) -> NamedElementDefinition:
    return NamedElementDefinition(name,
                                  file_ref_constant_container(file_ref_value, line_num, source_line))


def symbol_table_with_single_file_ref_value(
        name: str,
        file_ref_value: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                               relativity=RelOptionType.REL_CWD),
        line_num: int = 1,
        source_line: str = 'value def line') -> SymbolTable:
    return symbol_table_from_symbol_definitions(
        [file_ref_symbol_definition(name, file_ref_value, line_num, source_line)])


def symbol_reference(name: str,
                     value_restriction: ValueRestriction = AnySymbolTypeRestriction()) -> NamedElementReference:
    return NamedElementReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))


def entry(name: str,
          value_resolver: SymbolValueResolver = string_constant('string value'),
          line_num: int = 1,
          source_line: str = 'value def line') -> Entry:
    return Entry(name, NamedElementContainer(value_resolver,
                                             Line(line_num, source_line)))


def symbol_table_from_names(names: iter) -> SymbolTable:
    elements = [(name, string_constant_container(name,
                                                 source_line='source line for {}'.format(name)))
                for name in names]
    return SymbolTable(dict(elements))


def symbol_table_from_symbol_definitions(symbols: iter) -> SymbolTable:
    """
    :param symbols: [`SymbolDefinition`]
    """
    elements = [(vd.name, vd.resolver_container)
                for vd in symbols]
    return SymbolTable(dict(elements))
