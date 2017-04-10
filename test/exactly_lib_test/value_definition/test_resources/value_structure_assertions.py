from exactly_lib.value_definition import value_structure as stc
from exactly_lib.value_definition.concrete_values import SymbolValue
from exactly_lib_test.section_document.test_resources.assertions import equals_line
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources.concrete_value_assertions_2 import value_equals3


def equals_value_container(expected: stc.ValueContainer,
                           ignore_source_line: bool = True) -> asrt.ValueAssertion:
    component_assertions = []
    if not ignore_source_line:
        component_assertions.append(asrt.sub_component('source',
                                                       stc.ValueContainer.definition_source.fget,
                                                       equals_line(expected.definition_source)))
    expected_value = expected.value
    assert isinstance(expected_value, SymbolValue), 'All actual values must be SymbolValue'
    component_assertions.append(asrt.sub_component('value',
                                                   stc.ValueContainer.value.fget,
                                                   value_equals3(expected_value)))
    return asrt.is_instance_with(stc.ValueContainer,
                                 asrt.and_(component_assertions))


def equals_value_definition(expected: stc.ValueDefinition,
                            ignore_source_line: bool = True) -> asrt.ValueAssertion:
    return asrt.is_instance_with(stc.ValueDefinition,
                                 asrt.And([
                                     asrt.sub_component('name',
                                                        stc.ValueDefinition.name.fget,
                                                        asrt.equals(expected.name)),
                                     asrt.sub_component('value_container',
                                                        stc.ValueDefinition.value_container.fget,
                                                        equals_value_container(expected.value_container,
                                                                               ignore_source_line)),

                                 ])
                                 )
