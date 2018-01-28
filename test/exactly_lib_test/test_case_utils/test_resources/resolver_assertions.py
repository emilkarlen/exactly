from typing import Any

from exactly_lib.symbol import resolver_structure
from exactly_lib.symbol.resolver_structure import LineMatcherResolver
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.symbol.test_resources.type_assertions import is_resolver_of_logic_type
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def matches_resolver_of_logic_type(resolver_type: type,
                                   logic_value_type: LogicValueType,
                                   value_type: ValueType,
                                   resolved_value: asrt.ValueAssertion = asrt.anything_goes(),
                                   references: asrt.ValueAssertion = asrt.is_empty_list,
                                   symbols: symbol_table.SymbolTable = None) -> asrt.ValueAssertion[Any]:
    named_elements = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_value(resolver: LineMatcherResolver) -> LineMatcher:
        return resolver.resolve(named_elements)

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
