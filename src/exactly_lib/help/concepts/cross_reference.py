from exactly_lib.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help.entity_names import CONCEPT_ENTITY_TYPE_NAME


def concept_cross_ref(concept_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(CONCEPT_ENTITY_TYPE_NAME, concept_name)
