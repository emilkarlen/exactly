import unittest
from typing import Sequence

from exactly_lib.symbol import sdv_structure as rs
from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv, get_data_value_type
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv, get_logic_value_type
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv
from exactly_lib.type_system.value_type import TypeCategory, ValueType, LogicValueType, DataValueType
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def matches_sdv(sdv_type: ValueAssertion[rs.SymbolDependentValue],
                references: ValueAssertion[Sequence[SymbolReference]],
                resolved_value: ValueAssertion,
                custom: ValueAssertion[rs.SymbolDependentValue] = asrt.anything_goes(),
                symbols: SymbolTable = None) -> ValueAssertion[rs.SymbolDependentValue]:
    return _MatchesSymbolValueResolver(sdv_type,
                                       references,
                                       resolved_value,
                                       custom,
                                       symbol_table_from_none_or_value(symbols))


def is_sdv_of_data_type(data_value_type: DataValueType,
                        value_type: ValueType) -> ValueAssertion[rs.SymbolDependentValue]:
    return asrt.is_instance_with(DataTypeSdv,
                                 asrt.and_([
                                     asrt.sub_component('type_category',
                                                        rs.get_type_category,
                                                        asrt.is_(TypeCategory.DATA)),

                                     asrt.sub_component('data_value_type',
                                                        get_data_value_type,
                                                        asrt.is_(data_value_type)),

                                     asrt.sub_component('value_type',
                                                        rs.get_value_type,
                                                        asrt.is_(value_type)),
                                 ]))


def is_sdv_of_logic_type(logic_value_type: LogicValueType,
                         value_type: ValueType) -> ValueAssertion[rs.SymbolDependentValue]:
    return asrt.is_instance_with(LogicTypeSdv,
                                 asrt.and_([
                                     asrt.sub_component('type_category',
                                                        rs.get_type_category,
                                                        asrt.is_(TypeCategory.LOGIC)),

                                     asrt.sub_component('logic_value_type',
                                                        get_logic_value_type,
                                                        asrt.is_(logic_value_type)),

                                     asrt.sub_component('value_type',
                                                        rs.get_value_type,
                                                        asrt.is_(value_type)),
                                 ]))


def is_sdv_of_string_type() -> ValueAssertion[rs.SymbolDependentValue]:
    return is_sdv_of_data_type(DataValueType.STRING, ValueType.STRING)


def is_sdv_of_path_type() -> ValueAssertion[rs.SymbolDependentValue]:
    return is_sdv_of_data_type(DataValueType.PATH, ValueType.PATH)


def is_sdv_of_list_type() -> ValueAssertion[rs.SymbolDependentValue]:
    return is_sdv_of_data_type(DataValueType.LIST, ValueType.LIST)


def is_sdv_of_file_matcher_type() -> ValueAssertion[rs.SymbolDependentValue]:
    return is_sdv_of_logic_type(LogicValueType.FILE_MATCHER, ValueType.FILE_MATCHER)


def is_sdv_of_line_matcher_type() -> ValueAssertion[rs.SymbolDependentValue]:
    return is_sdv_of_logic_type(LogicValueType.LINE_MATCHER, ValueType.LINE_MATCHER)


def is_sdv_of_string_transformer_type() -> ValueAssertion[rs.SymbolDependentValue]:
    return is_sdv_of_logic_type(LogicValueType.STRING_TRANSFORMER, ValueType.STRING_TRANSFORMER)


def is_sdv_of_program_type() -> ValueAssertion[rs.SymbolDependentValue]:
    return is_sdv_of_logic_type(LogicValueType.PROGRAM, ValueType.PROGRAM)


def matches_sdv_of_string(references: ValueAssertion[Sequence[SymbolReference]],
                          resolved_value: ValueAssertion[StringDdv],
                          custom: ValueAssertion[StringSdv] = asrt.anything_goes(),
                          symbols: SymbolTable = None) -> ValueAssertion[rs.SymbolDependentValue]:
    return matches_sdv(is_sdv_of_string_type(),
                       references,
                       asrt.is_instance_with(StringDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_list(references: ValueAssertion[Sequence[SymbolReference]],
                        resolved_value: ValueAssertion[ListDdv],
                        custom: ValueAssertion[ListSdv] = asrt.anything_goes(),
                        symbols: SymbolTable = None) -> ValueAssertion[rs.SymbolDependentValue]:
    return matches_sdv(is_sdv_of_list_type(),
                       references,
                       asrt.is_instance_with(ListDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_path(references: ValueAssertion[Sequence[SymbolReference]],
                        resolved_value: ValueAssertion[PathDdv],
                        custom: ValueAssertion[PathSdv] = asrt.anything_goes(),
                        symbols: SymbolTable = None) -> ValueAssertion[rs.SymbolDependentValue]:
    return matches_sdv(is_sdv_of_path_type(),
                       references,
                       asrt.is_instance_with(PathDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_file_matcher(references: ValueAssertion[Sequence[SymbolReference]],
                                resolved_value: ValueAssertion[FileMatcherDdv],
                                custom: ValueAssertion[FileMatcherSdv] = asrt.anything_goes(),
                                symbols: SymbolTable = None) -> ValueAssertion[rs.SymbolDependentValue]:
    return matches_sdv(is_sdv_of_file_matcher_type(),
                       references,
                       asrt.is_instance_with(FileMatcherDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_line_matcher(references: ValueAssertion[Sequence[SymbolReference]],
                                resolved_value: ValueAssertion[DirDependentValue[LineMatcher]],
                                custom: ValueAssertion[LineMatcherSdv] = asrt.anything_goes(),
                                symbols: SymbolTable = None) -> ValueAssertion[rs.SymbolDependentValue]:
    return matches_sdv(is_sdv_of_line_matcher_type(),
                       references,
                       asrt.is_instance_with(MatcherDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_string_transformer(references: ValueAssertion[Sequence[SymbolReference]],
                                      resolved_value: ValueAssertion[StringTransformerDdv],
                                      custom: ValueAssertion[
                                          StringTransformerSdv] = asrt.anything_goes(),
                                      symbols: SymbolTable = None) -> ValueAssertion[rs.SymbolDependentValue]:
    return matches_sdv(is_sdv_of_string_transformer_type(),
                       references,
                       asrt.is_instance_with(StringTransformerDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_program(references: ValueAssertion[Sequence[SymbolReference]],
                           resolved_program_value: ValueAssertion[DirDependentValue],
                           custom: ValueAssertion[ProgramSdv] = asrt.anything_goes(),
                           symbols: SymbolTable = None) -> ValueAssertion[rs.SymbolDependentValue]:
    return matches_sdv(is_sdv_of_program_type(),
                       references,
                       asrt.is_instance_with(ProgramDdv, resolved_program_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


class _MatchesSymbolValueResolver(ValueAssertionBase[rs.SymbolDependentValue]):
    """Implements as class to make it possible to set break points"""

    def __init__(self,
                 sdv_type: ValueAssertion[rs.SymbolDependentValue],
                 references: ValueAssertion[Sequence[SymbolReference]],
                 resolved_value: ValueAssertion,
                 custom: ValueAssertion[rs.SymbolDependentValue],
                 symbols: SymbolTable):
        self.sdv_type = sdv_type
        self.references = references
        self.resolved_value = resolved_value
        self.custom = custom
        self.symbols = symbols

    def _apply(self,
               put: unittest.TestCase,
               value: rs.SymbolDependentValue,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, rs.SymbolDependentValue,
                             message_builder.apply("SDV type"))

        self.sdv_type.apply(put, value, message_builder)

        self.references.apply(put, value.references,
                              message_builder.for_sub_component('references'))

        self.custom.apply(put, value, message_builder)

        resolved_value = value.resolve(self.symbols)

        self.resolved_value.apply(put, resolved_value,
                                  message_builder.for_sub_component('resolved value'))
