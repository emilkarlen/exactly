from exactly_lib.symbol import list_resolver
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.assertion_utils import symbol_table_with_values_matching_references
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references, \
    equals_symbol_reference
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system_values.test_resources.string_value import equals_string_value


def equals_list_resolver_element(expected: list_resolver.Element,
                                 symbols: SymbolTable = None) -> asrt.ValueAssertion:
    if symbols is None:
        symbols = symbol_table_with_values_matching_references(list(expected.references))
    expected_resolved_value_list = expected.resolve(symbols)
    assertion_on_resolved_value = asrt.matches_sequence(
        [equals_string_value(sv) for sv in expected_resolved_value_list])
    component_assertions = [
        asrt.sub_component('references',
                           lambda x: list(x.references),
                           equals_symbol_references(list(expected.references))),
        asrt.sub_component('resolved value',
                           lambda x: x.resolve(symbols),
                           assertion_on_resolved_value),

    ]
    symbol_reference_assertion = asrt.is_none
    if expected.symbol_reference_if_is_symbol_reference is not None:
        symbol_reference_assertion = equals_symbol_reference(expected.symbol_reference_if_is_symbol_reference)
    symbol_reference_component_assertion = asrt.sub_component('symbol_reference_if_is_symbol_reference',
                                                              lambda x: x.symbol_reference_if_is_symbol_reference,
                                                              symbol_reference_assertion)
    component_assertions.append(symbol_reference_component_assertion)
    return asrt.is_instance_with(
        list_resolver.Element,
        asrt.and_(component_assertions))
