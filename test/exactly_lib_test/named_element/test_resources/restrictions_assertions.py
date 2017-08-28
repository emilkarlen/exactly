from exactly_lib.named_element.restriction import ElementTypeRestriction
from exactly_lib.type_system_values.value_type import ElementType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_element_type_restriction(expected: ElementType) -> asrt.ValueAssertion:
    """
    Assertion on a :class:`ReferenceRestrictions`,
    that it is a :class:`ElementTypeRestriction`,
    with a given :class:`ElementType`.
    """
    return asrt.is_instance_with(ElementTypeRestriction,
                                 asrt.sub_component('element_type',
                                                    ElementTypeRestriction.element_type.fget,
                                                    asrt.is_(expected)))
