from exactly_lib.value_definition import value_structure as stc
from exactly_lib_test.section_document.test_resources.assertions import equals_line
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources.concrete_value_assertion import equals_value


def equals_value_container(expected: stc.ValueContainer,
                           ignore_source_line: bool = True) -> asrt.ValueAssertion:
    component_assertions = []
    if not ignore_source_line:
        component_assertions.append(asrt.sub_component('source',
                                                       stc.ValueContainer.source.fget,
                                                       equals_line(expected.source)))
    component_assertions.append(asrt.sub_component('value',
                                                   stc.ValueContainer.value.fget,
                                                   equals_value(expected.value)))
    return asrt.is_instance_with(stc.ValueContainer,
                                 asrt.and_(component_assertions))


def equals_value_definition(expected: stc.ValueDefinition2,
                            ignore_source_line: bool = True) -> asrt.ValueAssertion:
    return asrt.is_instance_with(stc.ValueDefinition2,
                                 asrt.And([
                                     asrt.sub_component('name',
                                                        stc.ValueDefinition2.name.fget,
                                                        asrt.equals(expected.name)),
                                     asrt.sub_component('value_container',
                                                        stc.ValueDefinition2.value_container.fget,
                                                        equals_value_container(expected.value_container,
                                                                               ignore_source_line)),

                                 ])
                                 )


def equals_value_reference(expected_name: str,
                           value_restriction_assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.is_instance_with(stc.ValueReference2,
                                 asrt.and_([
                                     asrt.sub_component('name',
                                                        stc.ValueReference2.name.fget,
                                                        asrt.equals(expected_name)),
                                     asrt.sub_component('value_restriction',
                                                        stc.ValueReference2.value_restriction.fget,
                                                        value_restriction_assertion)
                                 ]))
