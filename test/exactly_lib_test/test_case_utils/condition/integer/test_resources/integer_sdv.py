from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import \
    is_reference_to_string_made_up_of_just_plain_strings
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def is_reference_to_symbol_in_expression(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return is_reference_to_string_made_up_of_just_plain_strings(symbol_name)
