from exactly_lib.symbol.data.restrictions import reference_restrictions
from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    equals_data_type_reference_restrictions
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def is_glob_pattern_string_reference_restrictions() -> ValueAssertion[ReferenceRestrictions]:
    return equals_data_type_reference_restrictions(
        reference_restrictions.is_any_data_type()
    )
