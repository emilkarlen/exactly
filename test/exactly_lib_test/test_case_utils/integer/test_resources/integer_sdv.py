from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    is_reference_to_string_made_up_of_just_strings


def is_reference_to_symbol_in_expression(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return is_reference_to_string_made_up_of_just_strings(symbol_name)
