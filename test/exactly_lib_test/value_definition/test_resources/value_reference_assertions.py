from exactly_lib.value_definition import value_structure as stc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_value_reference(expected_name: str,
                           value_restriction_assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.is_instance_with(stc.ValueReference,
                                 asrt.and_([
                                     asrt.sub_component('name',
                                                        stc.ValueReference.name.fget,
                                                        asrt.equals(expected_name)),
                                     asrt.sub_component('value_restriction',
                                                        stc.ValueReference.value_restriction.fget,
                                                        value_restriction_assertion)
                                 ]))
