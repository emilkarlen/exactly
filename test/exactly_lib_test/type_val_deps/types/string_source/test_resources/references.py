from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.any_.restrictions_assertions import \
    is_reference_restrictions__value_type
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_w_str_rend

IS_STRING_SOURCE_OR_STRING_REFERENCE_RESTRICTION = is_reference_restrictions__value_type(
    (ValueType.STRING_SOURCE, ValueType.STRING)
)

IS_STRING_REFERENCE_RESTRICTION = asrt_w_str_rend.is__w_str_rendering()


def is_reference_to__string_source_or_string(symbol_name: str) -> Assertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(
        symbol_name,
        IS_STRING_SOURCE_OR_STRING_REFERENCE_RESTRICTION,
    )


def is_reference_to__string(symbol_name: str) -> Assertion[SymbolReference]:
    return asrt_sym_ref.matches_reference_2(
        symbol_name,
        IS_STRING_REFERENCE_RESTRICTION,
    )
