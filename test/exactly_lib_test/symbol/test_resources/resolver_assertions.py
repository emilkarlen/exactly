from typing import Sequence

from exactly_lib.symbol import resolver_structure as rs
from exactly_lib.symbol.resolver_structure import LogicValueResolver, DataValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.value_type import TypeCategory, ValueType, LogicValueType, DataValueType
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def matches_resolver(resolver_type: asrt.ValueAssertion[rs.SymbolValueResolver],
                     references: asrt.ValueAssertion[Sequence[SymbolReference]],
                     resolved_value: asrt.ValueAssertion,
                     symbols: SymbolTable = None) -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    symbols = symbol_table_from_none_or_value(symbols)

    def resolve_value(resolver: rs.SymbolValueResolver):
        return resolver.resolve(symbols)

    def get_references(resolver: rs.SymbolValueResolver) -> Sequence[SymbolReference]:
        return resolver.references

    return asrt.is_instance_with_many(rs.SymbolValueResolver,
                                      [
                                          resolver_type,
                                          asrt.sub_component('references',
                                                             get_references,
                                                             references),
                                          asrt.sub_component('resolved value',
                                                             resolve_value,
                                                             resolved_value),
                                      ])


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


def is_resolver_of_string() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_data_type(DataValueType.STRING, ValueType.STRING)


def is_resolver_of_path() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_data_type(DataValueType.PATH, ValueType.PATH)


def is_resolver_of_list() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_data_type(DataValueType.LIST, ValueType.LIST)


def is_resolver_of_file_matcher() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_logic_type(LogicValueType.FILE_MATCHER, ValueType.FILE_MATCHER)


def is_resolver_of_line_matcher() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_logic_type(LogicValueType.LINE_MATCHER, ValueType.LINE_MATCHER)


def is_resolver_of_lines_transformer() -> asrt.ValueAssertion[rs.SymbolValueResolver]:
    return is_resolver_of_logic_type(LogicValueType.LINES_TRANSFORMER, ValueType.LINES_TRANSFORMER)
