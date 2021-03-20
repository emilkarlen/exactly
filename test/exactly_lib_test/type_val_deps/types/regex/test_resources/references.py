from exactly_lib.symbol.sdv_structure import SymbolReference, ReferenceRestrictions
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import symbol_reference_assertions as asrt_sym_ref, \
    data_restrictions_assertions as asrt_ref_rest


def is_reference_to__regex_string_part(symbol_name: str) -> Assertion[SymbolReference]:
    return asrt_sym_ref.is_reference_to__w_str_rendering(symbol_name)


def is_reference_restrictions__regex() -> Assertion[ReferenceRestrictions]:
    return asrt_ref_rest.is__w_str_rendering()
