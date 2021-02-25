from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    is_string__all_indirect_refs_are_strings
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_rest

IS_REFERENCE__STRING__W_ALL_INDIRECT_REFS_ARE_STRINGS = (
    asrt_rest.equals__w_str_rendering(
        is_string__all_indirect_refs_are_strings())
)


def is_sym_ref_to_string__w_all_indirect_refs_are_strings__usage(name_of_symbol: str) -> Assertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_symbol),
                                            IS_REFERENCE__STRING__W_ALL_INDIRECT_REFS_ARE_STRINGS)


def is_sym_ref_to_string__w_all_indirect_refs_are_strings(name_of_symbol: str,
                                                          ) -> Assertion[SymbolReference]:
    return asrt_sym_usage.matches_reference__ref(asrt.equals(name_of_symbol),
                                                 IS_REFERENCE__STRING__W_ALL_INDIRECT_REFS_ARE_STRINGS)
