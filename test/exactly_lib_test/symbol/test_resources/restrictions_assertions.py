from exactly_lib.symbol.restriction import ElementTypeRestriction, ValueTypeRestriction
from exactly_lib.type_system import value_type
from exactly_lib.type_system.value_type import ElementType, ValueType
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


def is_value_type_restriction(expected: ValueType) -> asrt.ValueAssertion:
    """
    Assertion on a :class:`ReferenceRestrictions`,
    that it is a :class:`ElementTypeRestriction`,
    with a given :class:`ElementType`.
    """
    expected_element_type = value_type.VALUE_TYPE_2_ELEMENT_TYPE[expected]
    return asrt.is_instance_with(ValueTypeRestriction,
                                 asrt.and_([
                                     asrt.sub_component('value_type',
                                                        ValueTypeRestriction.value_type.fget,
                                                        asrt.is_(expected)),
                                     asrt.sub_component('element_type',
                                                        ValueTypeRestriction.element_type.fget,
                                                        asrt.is_(expected_element_type)),
                                 ]),
                                 )
