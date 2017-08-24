from exactly_lib.named_element import resolver_structure as rs, named_element_usage as su
from exactly_lib.named_element.resolver_structure import NamedElementContainer
from exactly_lib_test.section_document.test_resources import assertions as asrt_sec_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def matches_container(assertion_on_resolver: asrt.ValueAssertion,
                      assertion_on_source: asrt.ValueAssertion = asrt_sec_doc.is_line(),
                      ) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        rs.NamedElementContainer,
        asrt.and_([
            asrt.sub_component('source',
                               rs.NamedElementContainer.definition_source.fget,
                               assertion_on_source),
            asrt.sub_component('resolver',
                               rs.NamedElementContainer.resolver.fget,
                               assertion_on_resolver)
        ]))


def matches_definition(assertion_on_name: asrt.ValueAssertion,
                       assertion_on_container: asrt.ValueAssertion,
                       ) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        su.NamedElementDefinition,
        asrt.And([
            asrt.sub_component('name',
                               su.NamedElementDefinition.name.fget,
                               asrt.is_instance_with(str,
                                                     assertion_on_name)),
            asrt.sub_component('resolver_container',
                               su.NamedElementDefinition.resolver_container.fget,
                               asrt.is_instance_with(NamedElementContainer,
                                                     assertion_on_container)),

        ])
    )


def matches_reference(expected_name: str,
                      assertion_on_restrictions: asrt.ValueAssertion = asrt.anything_goes()
                      ) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        su.NamedElementReference,
        asrt.and_([
            asrt.sub_component('name',
                               su.NamedElementReference.name.fget,
                               asrt.equals(expected_name)),
            asrt.sub_component('restrictions',
                               su.NamedElementReference.restrictions.fget,
                               assertion_on_restrictions)

        ]))
