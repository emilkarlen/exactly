import unittest
from typing import Sequence

from exactly_lib.symbol import resolver_structure as rs
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.symbol.resolver_structure import LogicValueResolver, DataValueResolver, StringTransformerResolver, \
    LineMatcherResolver, FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.lines_transformer import StringTransformerValue
from exactly_lib.type_system.logic.program.program_value import ProgramValue
from exactly_lib.type_system.value_type import TypeCategory, ValueType, LogicValueType, DataValueType
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def matches_resolver(resolver_type: asrt.ValueAssertion[rs.SymbolValueResolver],
                     references: asrt.ValueAssertion[Sequence[SymbolReference]],
                     resolved_value: asrt.ValueAssertion,
                     custom: asrt.ValueAssertion[rs.SymbolValueResolver] = asrt.anything_goes(),
                     symbols: SymbolTable = None) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return _MatchesSymbolValueResolver(resolver_type,
                                       references,
                                       resolved_value,
                                       custom,
                                       symbol_table_from_none_or_value(symbols))


def is_resolver_of_data_type(data_value_type: DataValueType,
                             value_type: ValueType) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return asrt.is_instance_with(DataValueResolver,
                                 asrt.and_([
                                     asrt.sub_component('type_category',
                                                        rs.get_type_category,
                                                        asrt.is_(TypeCategory.DATA)),

                                     asrt.sub_component('data_value_type',
                                                        rs.get_data_value_type,
                                                        asrt.is_(data_value_type)),

                                     asrt.sub_component('value_type',
                                                        rs.get_value_type,
                                                        asrt.is_(value_type)),
                                 ]))


def is_resolver_of_logic_type(logic_value_type: LogicValueType,
                              value_type: ValueType) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return asrt.is_instance_with(LogicValueResolver,
                                 asrt.and_([
                                     asrt.sub_component('type_category',
                                                        rs.get_type_category,
                                                        asrt.is_(TypeCategory.LOGIC)),

                                     asrt.sub_component('logic_value_type',
                                                        rs.get_logic_value_type,
                                                        asrt.is_(logic_value_type)),

                                     asrt.sub_component('value_type',
                                                        rs.get_value_type,
                                                        asrt.is_(value_type)),
                                 ]))


def is_resolver_of_string_type() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_data_type(DataValueType.STRING, ValueType.STRING)


def is_resolver_of_path_type() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_data_type(DataValueType.PATH, ValueType.PATH)


def is_resolver_of_list_type() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_data_type(DataValueType.LIST, ValueType.LIST)


def is_resolver_of_file_matcher_type() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_logic_type(LogicValueType.FILE_MATCHER, ValueType.FILE_MATCHER)


def is_resolver_of_line_matcher_type() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_logic_type(LogicValueType.LINE_MATCHER, ValueType.LINE_MATCHER)


def is_resolver_of_lines_transformer_type() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_logic_type(LogicValueType.LINES_TRANSFORMER, ValueType.LINES_TRANSFORMER)


def is_resolver_of_program_type() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_logic_type(LogicValueType.PROGRAM, ValueType.PROGRAM)


def matches_resolver_of_string(references: asrt.ValueAssertion[Sequence[SymbolReference]],
                               resolved_value: asrt.ValueAssertion[StringValue],
                               custom: asrt.ValueAssertion[StringResolver] = asrt.anything_goes(),
                               symbols: SymbolTable = None) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return matches_resolver(is_resolver_of_string_type(),
                            references,
                            asrt.is_instance_with(StringValue, resolved_value),
                            custom,
                            symbol_table_from_none_or_value(symbols))


def matches_resolver_of_list(references: asrt.ValueAssertion[Sequence[SymbolReference]],
                             resolved_value: asrt.ValueAssertion[ListValue],
                             custom: asrt.ValueAssertion[ListResolver] = asrt.anything_goes(),
                             symbols: SymbolTable = None) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return matches_resolver(is_resolver_of_list_type(),
                            references,
                            asrt.is_instance_with(ListValue, resolved_value),
                            custom,
                            symbol_table_from_none_or_value(symbols))


def matches_resolver_of_path(references: asrt.ValueAssertion[Sequence[SymbolReference]],
                             resolved_value: asrt.ValueAssertion[FileRef],
                             custom: asrt.ValueAssertion[FileRefResolver] = asrt.anything_goes(),
                             symbols: SymbolTable = None) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return matches_resolver(is_resolver_of_path_type(),
                            references,
                            asrt.is_instance_with(FileRef, resolved_value),
                            custom,
                            symbol_table_from_none_or_value(symbols))


def matches_resolver_of_file_matcher(references: asrt.ValueAssertion[Sequence[SymbolReference]],
                                     resolved_value: asrt.ValueAssertion[FileMatcher],
                                     custom: asrt.ValueAssertion[FileMatcherResolver] = asrt.anything_goes(),
                                     symbols: SymbolTable = None) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return matches_resolver(is_resolver_of_file_matcher_type(),
                            references,
                            asrt.is_instance_with(FileMatcher, resolved_value),
                            custom,
                            symbol_table_from_none_or_value(symbols))


def matches_resolver_of_line_matcher(references: asrt.ValueAssertion[Sequence[SymbolReference]],
                                     resolved_value: asrt.ValueAssertion[LineMatcher],
                                     custom: asrt.ValueAssertion[LineMatcherResolver] = asrt.anything_goes(),
                                     symbols: SymbolTable = None) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return matches_resolver(is_resolver_of_line_matcher_type(),
                            references,
                            asrt.is_instance_with(LineMatcher, resolved_value),
                            custom,
                            symbol_table_from_none_or_value(symbols))


def matches_resolver_of_lines_transformer(references: asrt.ValueAssertion[Sequence[SymbolReference]],
                                          resolved_value: asrt.ValueAssertion[StringTransformerValue],
                                          custom: asrt.ValueAssertion[StringTransformerResolver] = asrt.anything_goes(),
                                          symbols: SymbolTable = None) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return matches_resolver(is_resolver_of_lines_transformer_type(),
                            references,
                            asrt.is_instance_with(StringTransformerValue, resolved_value),
                            custom,
                            symbol_table_from_none_or_value(symbols))


def matches_resolver_of_program(references: asrt.ValueAssertion[Sequence[SymbolReference]],
                                resolved_program_value: asrt.ValueAssertion[DirDependentValue],
                                custom: asrt.ValueAssertion[ProgramResolver] = asrt.anything_goes(),
                                symbols: SymbolTable = None) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return matches_resolver(is_resolver_of_program_type(),
                            references,
                            asrt.is_instance_with(ProgramValue, resolved_program_value),
                            custom,
                            symbol_table_from_none_or_value(symbols))


class _MatchesSymbolValueResolver(asrt.ValueAssertion[rs.SymbolValueResolver]):
    """Implements as class to make it possible to set break points"""

    def __init__(self,
                 resolver_type: asrt.ValueAssertion[rs.SymbolValueResolver],
                 references: asrt.ValueAssertion[Sequence[SymbolReference]],
                 resolved_value: asrt.ValueAssertion,
                 custom: asrt.ValueAssertion[rs.SymbolValueResolver],
                 symbols: SymbolTable):
        self.resolver_type = resolver_type
        self.references = references
        self.resolved_value = resolved_value
        self.custom = custom
        self.symbols = symbols

    def apply(self,
              put: unittest.TestCase,
              value: rs.SymbolValueResolver,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, rs.SymbolValueResolver,
                             message_builder.apply("resolver type"))

        self.resolver_type.apply(put, value, message_builder)

        self.references.apply(put, value.references,
                              message_builder.for_sub_component('references'))

        self.custom.apply(put, value, message_builder)

        resolved_value = value.resolve(self.symbols)

        self.resolved_value.apply(put, resolved_value,
                                  message_builder.for_sub_component('resolved value'))
