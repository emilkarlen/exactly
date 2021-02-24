from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.data_restrictions_assertions import \
    equals_reference_restrictions__w_str_rendering


def is_reference_restrictions__glob_pattern_string() -> Assertion[ReferenceRestrictions]:
    return equals_reference_restrictions__w_str_rendering(
        reference_restrictions.is_any_type_w_str_rendering()
    )
