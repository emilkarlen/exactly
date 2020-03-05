import unittest
from typing import Sequence

from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv, get_data_value_type
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.file_matcher import FileMatcherStv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherStv
from exactly_lib.symbol.logic.line_matcher import LineMatcherStv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDependentTypeValue
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.files_matcher import FilesMatcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv
from exactly_lib.type_system.value_type import TypeCategory, ValueType, LogicValueType, DataValueType
from exactly_lib.util.file_utils import TmpDirFileSpace, TmpDirFileSpaceThatMustNoBeUsed
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.symbol.test_resources.sdv_structure_assertions import is_stv_of_logic_type
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.matcher.test_resources.assertions import matches_matcher_stv
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def matches_sdv(sdv_type: ValueAssertion[SymbolDependentTypeValue],
                references: ValueAssertion[Sequence[SymbolReference]],
                resolved_value: ValueAssertion,
                custom: ValueAssertion[SymbolDependentTypeValue] = asrt.anything_goes(),
                symbols: SymbolTable = None) -> ValueAssertion[SymbolDependentTypeValue]:
    return _MatchesStv(sdv_type,
                       references,
                       resolved_value,
                       custom,
                       symbol_table_from_none_or_value(symbols))


def is_sdv_of_data_type(data_value_type: DataValueType,
                        value_type: ValueType) -> ValueAssertion[SymbolDependentTypeValue]:
    return asrt.is_instance_with(DataTypeSdv,
                                 asrt.and_([
                                     asrt.sub_component('type_category',
                                                        sdv_structure.get_type_category,
                                                        asrt.is_(TypeCategory.DATA)),

                                     asrt.sub_component('data_value_type',
                                                        get_data_value_type,
                                                        asrt.is_(data_value_type)),

                                     asrt.sub_component('value_type',
                                                        sdv_structure.get_value_type,
                                                        asrt.is_(value_type)),
                                 ]))


def is_sdv_of_string_type() -> ValueAssertion[SymbolDependentTypeValue]:
    return is_sdv_of_data_type(DataValueType.STRING, ValueType.STRING)


def is_sdv_of_path_type() -> ValueAssertion[SymbolDependentTypeValue]:
    return is_sdv_of_data_type(DataValueType.PATH, ValueType.PATH)


def is_sdv_of_list_type() -> ValueAssertion[SymbolDependentTypeValue]:
    return is_sdv_of_data_type(DataValueType.LIST, ValueType.LIST)


def is_sdv_of_file_matcher_type() -> ValueAssertion[SymbolDependentTypeValue]:
    return is_stv_of_logic_type(LogicValueType.FILE_MATCHER)


def is_sdv_of_line_matcher_type() -> ValueAssertion[SymbolDependentTypeValue]:
    return is_stv_of_logic_type(LogicValueType.LINE_MATCHER)


def is_sdv_of_string_transformer_type() -> ValueAssertion[SymbolDependentTypeValue]:
    return is_stv_of_logic_type(LogicValueType.STRING_TRANSFORMER)


def is_sdv_of_program_type() -> ValueAssertion[SymbolDependentTypeValue]:
    return is_stv_of_logic_type(LogicValueType.PROGRAM)


def matches_sdv_of_string(references: ValueAssertion[Sequence[SymbolReference]],
                          resolved_value: ValueAssertion[StringDdv],
                          custom: ValueAssertion[StringSdv] = asrt.anything_goes(),
                          symbols: SymbolTable = None) -> ValueAssertion[SymbolDependentTypeValue]:
    return matches_sdv(is_sdv_of_string_type(),
                       references,
                       asrt.is_instance_with(StringDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_list(references: ValueAssertion[Sequence[SymbolReference]],
                        resolved_value: ValueAssertion[ListDdv],
                        custom: ValueAssertion[ListSdv] = asrt.anything_goes(),
                        symbols: SymbolTable = None) -> ValueAssertion[SymbolDependentTypeValue]:
    return matches_sdv(is_sdv_of_list_type(),
                       references,
                       asrt.is_instance_with(ListDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_path(references: ValueAssertion[Sequence[SymbolReference]],
                        resolved_value: ValueAssertion[PathDdv],
                        custom: ValueAssertion[PathSdv] = asrt.anything_goes(),
                        symbols: SymbolTable = None) -> ValueAssertion[SymbolDependentTypeValue]:
    return matches_sdv(is_sdv_of_path_type(),
                       references,
                       asrt.is_instance_with(PathDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_stv_of_file_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                primitive_value: ValueAssertion[FileMatcher] = asrt.anything_goes(),
                                symbols: SymbolTable = None,
                                tcds: Tcds = fake_tcds(),
                                tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
                                ) -> ValueAssertion[SymbolDependentTypeValue]:
    return matches_matcher_stv(
        FileMatcherStv,
        LogicValueType.FILE_MATCHER,
        primitive_value,
        references,
        symbol_table_from_none_or_value(symbols),
        tcds,
        tmp_file_space,
    )


def matches_stv_of_files_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                 primitive_value: ValueAssertion[FilesMatcher] = asrt.anything_goes(),
                                 symbols: SymbolTable = None,
                                 tcds: Tcds = fake_tcds(),
                                 tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
                                 ) -> ValueAssertion[SymbolDependentTypeValue]:
    return matches_matcher_stv(
        FilesMatcherStv,
        LogicValueType.FILES_MATCHER,
        primitive_value,
        references,
        symbol_table_from_none_or_value(symbols),
        tcds,
        tmp_file_space,
    )


def matches_stv_of_line_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                primitive_value: ValueAssertion[LineMatcher] = asrt.anything_goes(),
                                symbols: SymbolTable = None,
                                tcds: Tcds = fake_tcds(),
                                tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
                                ) -> ValueAssertion[SymbolDependentTypeValue]:
    return matches_matcher_stv(
        LineMatcherStv,
        LogicValueType.LINE_MATCHER,
        primitive_value,
        references,
        symbol_table_from_none_or_value(symbols),
        tcds,
        tmp_file_space,
    )


def matches_stv_of_string_transformer(references: ValueAssertion[Sequence[SymbolReference]],
                                      resolved_value: ValueAssertion[StringTransformerDdv],
                                      custom: ValueAssertion[
                                          StringTransformerSdv] = asrt.anything_goes(),
                                      symbols: SymbolTable = None) -> ValueAssertion[SymbolDependentTypeValue]:
    return matches_sdv(is_sdv_of_string_transformer_type(),
                       references,
                       asrt.is_instance_with(StringTransformerDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_stv_of_program(references: ValueAssertion[Sequence[SymbolReference]],
                           resolved_program_value: ValueAssertion[DirDependentValue],
                           custom: ValueAssertion[ProgramSdv] = asrt.anything_goes(),
                           symbols: SymbolTable = None) -> ValueAssertion[SymbolDependentTypeValue]:
    return matches_sdv(is_sdv_of_program_type(),
                       references,
                       asrt.is_instance_with(ProgramDdv, resolved_program_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


class _MatchesStv(ValueAssertionBase[SymbolDependentTypeValue]):
    """Implements as class to make it possible to set break points"""

    def __init__(self,
                 sdv_type: ValueAssertion[SymbolDependentTypeValue],
                 references: ValueAssertion[Sequence[SymbolReference]],
                 resolved_value: ValueAssertion,
                 custom: ValueAssertion[SymbolDependentTypeValue],
                 symbols: SymbolTable):
        self.sdv_type = sdv_type
        self.references = references
        self.resolved_value = resolved_value
        self.custom = custom
        self.symbols = symbols

    def _apply(self,
               put: unittest.TestCase,
               value: SymbolDependentTypeValue,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, SymbolDependentTypeValue,
                             message_builder.apply("SDV type"))

        self.sdv_type.apply(put, value, message_builder)

        self.references.apply(put, value.references,
                              message_builder.for_sub_component('references'))

        self.custom.apply(put, value, message_builder)

        resolved_value = value.resolve(self.symbols)

        self.resolved_value.apply(put, resolved_value,
                                  message_builder.for_sub_component('resolved value'))
