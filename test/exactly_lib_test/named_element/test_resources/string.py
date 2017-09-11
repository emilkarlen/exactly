from exactly_lib.named_element.symbol.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib_test.named_element.symbol.restrictions.test_resources.concrete_restriction_assertion import \
    equals_symbol_reference_restrictions
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions as asrt_ne
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION = equals_symbol_reference_restrictions(
    string_made_up_by_just_strings())


def is_string_made_up_of_just_strings_reference_to(name_of_symbol: str) -> asrt.ValueAssertion:
    return asrt_ne.matches_reference(asrt.equals(name_of_symbol),
                                     IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION)
