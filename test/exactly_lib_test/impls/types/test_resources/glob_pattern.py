from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib.type_val_deps.sym_ref.data import reference_restrictions
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.data.data_restrictions_assertions import \
    equals_reference_restrictions__convertible_to_string


def is_reference_restrictions__glob_pattern_string() -> Assertion[ReferenceRestrictions]:
    return equals_reference_restrictions__convertible_to_string(
        reference_restrictions.is_type_convertible_to_string()
    )
