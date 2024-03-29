from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.any_.restrictions_assertions import \
    is_reference_restrictions__value_type

IS_STRING_MATCHER_REFERENCE_RESTRICTION = is_reference_restrictions__value_type((ValueType.STRING_MATCHER,))


def is_reference_to_string_matcher__usage(name_of_matcher: str) -> Assertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                            IS_STRING_MATCHER_REFERENCE_RESTRICTION)


def is_reference_to_string_matcher(name_of_matcher: str) -> Assertion[SymbolReference]:
    return asrt.is_instance_with(
        SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                         IS_STRING_MATCHER_REFERENCE_RESTRICTION)
    )
