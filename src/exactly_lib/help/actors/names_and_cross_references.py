from exactly_lib.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help.entity_names import ACTOR_ENTITY_TYPE_NAME


def actor_cross_ref(entity_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(ACTOR_ENTITY_TYPE_NAME, entity_name)


SINGLE_COMMAND_LINE_ACTOR__NAME = 'single command line'
SINGLE_COMMAND_LINE_ACTOR__CROSS_REF = actor_cross_ref(SINGLE_COMMAND_LINE_ACTOR__NAME)

ALL_ACTORS__CROSS_REFS = [
    SINGLE_COMMAND_LINE_ACTOR__CROSS_REF
]
