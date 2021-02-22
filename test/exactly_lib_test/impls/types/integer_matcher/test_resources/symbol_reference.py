from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.data.data_restrictions_assertions import \
    is_reference_restrictions__string_made_up_of_just_strings


def is_reference_restrictions__integer_expression() -> Assertion[ReferenceRestrictions]:
    return is_reference_restrictions__string_made_up_of_just_strings()
