from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.sym_ref.test_resources.restrictions_assertions import is_value_type_restriction

IS_STRING_TRANSFORMER_REFERENCE_RESTRICTION = is_value_type_restriction((ValueType.STRING_TRANSFORMER,))


def is_reference_to_string_transformer__usage(name_of_transformer: str) -> Assertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_transformer),
                                            IS_STRING_TRANSFORMER_REFERENCE_RESTRICTION)


def is_reference_to_string_transformer(name_of_transformer: str) -> Assertion[SymbolReference]:
    return asrt.is_instance_with(SymbolReference,
                                 asrt_sym_usage.matches_reference(asrt.equals(name_of_transformer),
                                                                  IS_STRING_TRANSFORMER_REFERENCE_RESTRICTION)
                                 )
