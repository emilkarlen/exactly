from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    is_string_made_up_of_just_strings_reference_restrictions
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def is_integer_expression_string() -> ValueAssertion[ReferenceRestrictions]:
    return is_string_made_up_of_just_strings_reference_restrictions()
