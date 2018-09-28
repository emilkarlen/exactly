from exactly_lib.definitions.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import EntityTypeNames
from exactly_lib_test.definitions.test_resources import cross_reference_id_va as asrt_cross_ref
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources.name import equals_name_with_gender


def equals_entity_cross_ref(entity_type_names: EntityTypeNames,
                            entity_name: str) -> ValueAssertion:
    return asrt.is_instance_with(EntityCrossReferenceId,
                                 asrt.and_([
                                     asrt_cross_ref.is_any,
                                     asrt.sub_component('entity-name',
                                                        EntityCrossReferenceId.entity_name.fget,
                                                        asrt.equals(entity_name)
                                                        ),
                                     asrt.sub_component('entity-type-names',
                                                        EntityCrossReferenceId.entity_type_names.fget,
                                                        equals_entity_type_names(entity_type_names)
                                                        ),
                                     asrt.sub_component('entity_type_identifier',
                                                        EntityCrossReferenceId.entity_type_identifier.fget,
                                                        asrt.equals(entity_type_names.identifier)
                                                        ),
                                     asrt.sub_component('entity_type_presentation_name',
                                                        EntityCrossReferenceId.entity_type_presentation_name.fget,
                                                        asrt.equals(entity_type_names.name.singular)
                                                        ),
                                 ]))


def equals_entity_type_names(entity_type_names: EntityTypeNames) -> ValueAssertion:
    return asrt.is_instance_with(EntityTypeNames,
                                 asrt.and_([
                                     asrt.sub_component('identifier',
                                                        EntityTypeNames.identifier.fget,
                                                        asrt.equals(entity_type_names.identifier)
                                                        ),
                                     asrt.sub_component('name',
                                                        EntityTypeNames.name.fget,
                                                        equals_name_with_gender(entity_type_names.name)
                                                        ),
                                 ]))
