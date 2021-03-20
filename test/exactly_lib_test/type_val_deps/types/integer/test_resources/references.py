from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_reference_assertions import \
    is_reference_to_string__w_all_indirect_refs_are_strings


def is_reference_to_symbol_in_expression(symbol_name: str) -> Assertion[SymbolReference]:
    return is_reference_to_string__w_all_indirect_refs_are_strings(symbol_name)
