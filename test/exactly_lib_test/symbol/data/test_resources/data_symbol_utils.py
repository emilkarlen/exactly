from typing import Iterable, Tuple

from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction
from exactly_lib.symbol.data.value_restriction import ValueRestriction
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.data import path_ddv as _path
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.value_type import DataValueType
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib_test.symbol.data.test_resources.list_sdvs import ListSdvTestImplForConstantListDdv
from exactly_lib_test.symbol.data.test_resources.sdvs import ConstantSdv
from exactly_lib_test.symbol.test_resources.symbol_utils import single_line_sequence
from exactly_lib_test.test_case_file_structure.test_resources.simple_path import path_test_impl


def container(value_sdv: DataTypeSdv,
              line_num: int = 1,
              source_line: str = 'value def line') -> SymbolContainer:
    return SymbolContainer(value_sdv,
                           single_line_sequence(line_num, source_line))


def container_of_builtin(value_sdv: DataTypeSdv) -> SymbolContainer:
    return sdv_structure.container_of_builtin(value_sdv)


def string_constant_container(constant_str: str,
                              line_num: int = 1,
                              source_line: str = 'value def line') -> SymbolContainer:
    return SymbolContainer(string_sdvs.str_constant(constant_str),
                           single_line_sequence(line_num, source_line))


def string_ddv_constant_container2(string_ddv: StringDdv,
                                   line_num: int = 1,
                                   source_line: str = 'value def line') -> SymbolContainer:
    return SymbolContainer(ConstantSdv(DataValueType.STRING,
                                       string_ddv),
                           single_line_sequence(line_num, source_line))


def string_symbol_definition(name: str, constant_str: str = 'string value') -> SymbolDefinition:
    return SymbolDefinition(name,
                            string_constant_container(constant_str))


def string_ddv_symbol_definition(name: str, string_ddv: StringDdv) -> SymbolDefinition:
    return SymbolDefinition(name,
                            string_ddv_constant_container2(string_ddv))


def symbol_table_with_single_string_value(name: str, string_value: str = 'string value') -> SymbolTable:
    return symbol_table_from_symbol_definitions([string_symbol_definition(name, string_value)])


def symbol_table_with_string_values(name_and_value_pairs: Iterable[Tuple[str, str]]) -> SymbolTable:
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


def list_ddv_constant_container(list_ddv: ListDdv,
                                line_num: int = 1,
                                source_line: str = 'value def line') -> SymbolContainer:
    return SymbolContainer(ListSdvTestImplForConstantListDdv(list_ddv),
                           single_line_sequence(line_num, source_line))


def list_symbol_definition(name: str, resolved_value: ListDdv) -> SymbolDefinition:
    return SymbolDefinition(name, list_ddv_constant_container(resolved_value))


def symbol_table_with_single_list_value(symbol_name: str, resolved_value: ListDdv) -> SymbolTable:
    return symbol_table_from_symbol_definitions([list_symbol_definition(symbol_name, resolved_value)])


def path_constant_container(
        path_value: _path.PathDdv = path_test_impl('file-name-rel-cd',
                                                   relativity=RelOptionType.REL_CWD),
        line_num: int = 1,
        source_line: str = 'value def line') -> SymbolContainer:
    return SymbolContainer(path_sdvs.constant(path_value),
                           single_line_sequence(line_num, source_line))


def path_sdv_container(path_sdv: PathSdv,
                       line_num: int = 1,
                       source_line: str = 'value def line') -> SymbolContainer:
    return SymbolContainer(path_sdv,
                           single_line_sequence(line_num, source_line))


def path_symbol_definition(
        name: str,
        path_value: _path.PathDdv = path_test_impl('file-name-rel-cd',
                                                   relativity=RelOptionType.REL_CWD),
        line_num: int = 1,
        source_line: str = 'value def line'
) -> SymbolDefinition:
    return SymbolDefinition(name,
                            path_constant_container(path_value, line_num, source_line))


def symbol_table_with_single_path_value(
        name: str,
        path_value: _path.PathDdv = path_test_impl('file-name-rel-cd',
                                                   relativity=RelOptionType.REL_CWD),
        line_num: int = 1,
        source_line: str = 'value def line') -> SymbolTable:
    return symbol_table_from_symbol_definitions(
        [path_symbol_definition(name, path_value, line_num, source_line)])


def symbol_reference(name: str,
                     value_restriction: ValueRestriction = AnyDataTypeRestriction()) -> SymbolReference:
    return SymbolReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))


def entry(name: str,
          value_sdv: DataTypeSdv = string_sdvs.str_constant('string value'),
          line_num: int = 1,
          source_line: str = 'value def line') -> Entry:
    return Entry(name, SymbolContainer(value_sdv,
                                       single_line_sequence(line_num, source_line)))


def symbol_table_from_names(names: Iterable[str]) -> SymbolTable:
    elements = [(name, string_constant_container(name,
                                                 source_line='source line for {}'.format(name)))
                for name in names]
    return SymbolTable(dict(elements))


def symbol_table_from_symbol_definitions(symbols: Iterable[SymbolDefinition]) -> SymbolTable:
    elements = [(vd.name, vd.symbol_container)
                for vd in symbols]
    return SymbolTable(dict(elements))
