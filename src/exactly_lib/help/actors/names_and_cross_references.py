from exactly_lib.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help.entity_names import ACTOR_ENTITY_TYPE_NAME
from exactly_lib.help.utils.name_and_cross_ref import SingularNameAndCrossReferenceId


def actor_cross_ref(actor_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(ACTOR_ENTITY_TYPE_NAME, actor_name)


def name_and_ref_target(name: str) -> SingularNameAndCrossReferenceId:
    return SingularNameAndCrossReferenceId(name, actor_cross_ref(name))


SINGLE_COMMAND_LINE_ACTOR = name_and_ref_target('single command line')

ALL_ACTORS = [
    SINGLE_COMMAND_LINE_ACTOR,
]


def all_actor_cross_refs() -> list:
    return [x.cross_reference_target
            for x in ALL_ACTORS]
