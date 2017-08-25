from exactly_lib.named_element.resolver_structure import ElementType
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions as asrt_ne
from exactly_lib_test.named_element.test_resources.restrictions_assertions import is_element_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

IS_FILE_REFERENCE_RESTRICTION = is_element_type_restriction(ElementType.FILE_SELECTOR)


def is_file_selector_reference_to(name_of_file_selector: str) -> asrt.ValueAssertion:
    return asrt_ne.matches_reference(asrt.equals(name_of_file_selector),
                                     is_element_type_restriction(ElementType.FILE_SELECTOR))
