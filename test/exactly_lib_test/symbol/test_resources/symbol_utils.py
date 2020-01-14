import pathlib
from typing import Sequence, Mapping

from exactly_lib.section_document.source_location import FileLocationInfo, SourceLocationInfo
from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction
from exactly_lib.symbol.data.value_restriction import ValueRestriction
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolDependentValue
from exactly_lib.symbol.symbol_usage import SymbolReference, SymbolDefinition
from exactly_lib.util import line_source
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def container(value_sdv: SymbolDependentValue,
              line_num: int = 1,
              source_line: str = 'value def line') -> SymbolContainer:
    return SymbolContainer(value_sdv,
                           single_line_sequence(line_num, source_line))


def container_of_builtin(value_sdv: SymbolDependentValue) -> SymbolContainer:
    return sdv_structure.container_of_builtin(value_sdv)


def element_reference(name: str,
                      value_restriction: ValueRestriction = AnyDataTypeRestriction()) -> SymbolReference:
    return SymbolReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))


def entry_with_arbitrary_element(name: str,
                                 value_sdv: DataTypeSdv = string_sdvs.str_constant('string value'),
                                 line_num: int = 1,
                                 source_line: str = 'value def line') -> Entry:
    return Entry(name, SymbolContainer(value_sdv,
                                       single_line_sequence(line_num, source_line)))


def definition_with_arbitrary_element(name: str,
                                      value_sdv: DataTypeSdv = string_sdvs.str_constant('string value'),
                                      line_num: int = 1,
                                      source_line: str = 'value def line') -> SymbolDefinition:
    return SymbolDefinition(name, SymbolContainer(value_sdv,
                                                  single_line_sequence(line_num, source_line)))


def symbol_table_from_symbol_definitions(definitions: Sequence[SymbolDefinition]) -> SymbolTable:
    elements = [(sym_def.name, sym_def.symbol_container)
                for sym_def in definitions]
    return SymbolTable(dict(elements))


def symbol_table_from_name_and_containers(name_and_containers: Sequence[NameAndValue[SymbolContainer]]) -> SymbolTable:
    return SymbolTable({
        nac.name: nac.value
        for nac in name_and_containers
    })


def symbol_table_from_name_and_sdvs(
        name_and_sdvs: Sequence[NameAndValue[SymbolDependentValue]]) -> SymbolTable:
    return SymbolTable({
        nar.name: container(nar.value)
        for nar in name_and_sdvs
    })


def symbol_table_from_name_and_sdv_mapping(
        name_and_sdvs: Mapping[str, SymbolDependentValue]) -> SymbolTable:
    return SymbolTable({
        n_sdv[0]: container(n_sdv[1])
        for n_sdv in name_and_sdvs.items()
    })


_FL = FileLocationInfo(pathlib.Path('/'))


def single_line_sequence(line_number: int, line: str) -> SourceLocationInfo:
    return source_info_for_line_sequence(line_source.single_line_sequence(line_number, line))


def source_info_for_line_sequence(source: line_source.LineSequence) -> SourceLocationInfo:
    return _FL.source_location_info_for(source)
