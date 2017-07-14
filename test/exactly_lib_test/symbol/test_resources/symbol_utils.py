from exactly_lib.symbol.concrete_restrictions import NoRestriction, ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.symbol.string_resolver import string_constant
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolReference
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.symbol.value_restriction import ValueRestriction
from exactly_lib.symbol.value_structure import ResolverContainer, SymbolValueResolver
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system_values import file_ref as _file_ref
from exactly_lib.type_system_values.list_value import ListValue
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib_test.symbol.test_resources.list_values import ListResolverTestImplForConstantListValue
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl


def container(value: SymbolValueResolver,
              line_num: int = 1,
              source_line: str = 'value def line') -> ResolverContainer:
    return ResolverContainer(Line(line_num, source_line),
                             value)


def string_value_constant_container(string_value: str,
                                    line_num: int = 1,
                                    source_line: str = 'value def line') -> ResolverContainer:
    return ResolverContainer(Line(line_num, source_line),
                             string_constant(string_value))


def string_symbol_definition(name: str, string_value: str = 'string value') -> SymbolDefinition:
    return SymbolDefinition(name, string_value_constant_container(string_value))


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
                 string_value_constant_container(name_and_value.value))
                for name_and_value in name_and_value_list]
    return SymbolTable(dict(elements))


def list_value_constant_container(list_value: ListValue,
                                  line_num: int = 1,
                                  source_line: str = 'value def line') -> ResolverContainer:
    return ResolverContainer(Line(line_num, source_line),
                             ListResolverTestImplForConstantListValue(list_value))


def file_ref_constant_container(
        file_ref: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                         relativity=RelOptionType.REL_CWD),
        line_num: int = 1,
        source_line: str = 'value def line') -> ResolverContainer:
    return ResolverContainer(Line(line_num, source_line),
                             FileRefConstant(file_ref))


def file_ref_resolver_container(file_ref_resolver: FileRefResolver,
                                line_num: int = 1,
                                source_line: str = 'value def line') -> ResolverContainer:
    return ResolverContainer(Line(line_num, source_line),
                             file_ref_resolver)


def file_ref_symbol_definition(name: str,
                               file_ref: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                                                relativity=RelOptionType.REL_CWD),
                               line_num: int = 1,
                               source_line: str = 'value def line'
                               ) -> SymbolDefinition:
    return SymbolDefinition(name, file_ref_constant_container(file_ref, line_num, source_line))


def symbol_table_with_single_file_ref_value(
        name: str,
        file_ref: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                         relativity=RelOptionType.REL_CWD),
        line_num: int = 1,
        source_line: str = 'value def line') -> SymbolTable:
    return symbol_table_from_symbol_definitions([file_ref_symbol_definition(name, file_ref, line_num, source_line)])


def symbol_reference(name: str, value_restriction: ValueRestriction = NoRestriction()) -> SymbolReference:
    return SymbolReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))


def entry(name: str, value: SymbolValueResolver = string_constant('string value'),
          line_num: int = 1,
          source_line: str = 'value def line') -> Entry:
    return Entry(name, ResolverContainer(Line(line_num, source_line), value))


def symbol_table_from_names(names: iter) -> SymbolTable:
    elements = [(name, string_value_constant_container(name, source_line='source line for {}'.format(name)))
                for name in names]
    return SymbolTable(dict(elements))


def symbol_table_from_symbol_definitions(symbols: iter) -> SymbolTable:
    """
    :param symbols: [`SymbolDefinition`]
    """
    elements = [(vd.name, vd.resolver_container)
                for vd in symbols]
    return SymbolTable(dict(elements))
