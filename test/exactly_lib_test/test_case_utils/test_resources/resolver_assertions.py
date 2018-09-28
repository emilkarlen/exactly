from typing import Any, Sequence, Type

from exactly_lib.symbol import resolver_structure
from exactly_lib.symbol.resolver_structure import LogicValueResolver, SymbolValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.symbol.test_resources.resolver_assertions import is_resolver_of_logic_type
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_resolver_of_logic_type(resolver_type: type,
                                   logic_value_type: LogicValueType,
                                   value_type: ValueType,
                                   resolved_value: ValueAssertion = asrt.anything_goes(),
                                   references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                                   symbols: symbol_table.SymbolTable = None) -> ValueAssertion[Any]:
    symbols = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_value(resolver: LogicValueResolver) -> LineMatcher:
        return resolver.resolve(symbols)

    return asrt.is_instance_with(resolver_type,
                                 asrt.and_([
                                     is_resolver_of_logic_type(logic_value_type,
                                                               value_type),

                                     asrt.on_transformed(resolve_value,
                                                         resolved_value),

                                     asrt.sub_component('references',
                                                        resolver_structure.get_references,
                                                        references),
                                 ]))


def matches_resolver_of_logic_type2(resolver_type: Type,
                                    logic_value_type: LogicValueType,
                                    value_type: ValueType,
                                    resolved_value: ValueAssertion = asrt.anything_goes(),
                                    references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                                    symbols: symbol_table.SymbolTable = None
                                    ) -> ValueAssertion[LogicValueResolver]:
    symbols = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_value(resolver: SymbolValueResolver):
        return resolver.resolve(symbols).value_when_no_dir_dependencies()

    return asrt.is_instance_with(resolver_type,
                                 asrt.and_([
                                     is_resolver_of_logic_type(logic_value_type,
                                                               value_type),

                                     asrt.on_transformed(resolve_value,
                                                         resolved_value),

                                     asrt.sub_component('references',
                                                        resolver_structure.get_references,
                                                        references),
                                 ]))
