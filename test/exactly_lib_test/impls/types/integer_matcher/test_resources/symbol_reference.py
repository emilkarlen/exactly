from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_data_rest


def is_reference_restrictions__integer_expression() -> Assertion[ReferenceRestrictions]:
    return asrt_data_rest.is__string__w_all_indirect_refs_are_strings()
