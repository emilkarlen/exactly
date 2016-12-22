from exactly_lib.common.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help.entity_names import ACTOR_ENTITY_TYPE_NAME
from exactly_lib.help.utils.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.help.utils.phase_names import ACT_PHASE_NAME


def actor_cross_ref(actor_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(ACTOR_ENTITY_TYPE_NAME, actor_name)


def name_and_ref_target(name: str,
                        single_line_description_str: str) -> SingularNameAndCrossReferenceId:
    return SingularNameAndCrossReferenceId(name, single_line_description_str, actor_cross_ref(name))


COMMAND_LINE_ACTOR = name_and_ref_target(
    'command line',
    'Executes a command line - either an executable file or a shell command')
SOURCE_INTERPRETER_ACTOR = name_and_ref_target(
    'source interpreter',
    'Treats the {act_phase} phase as source code to be executed by an interpreter'.format(
        act_phase=ACT_PHASE_NAME.syntax))
FILE_INTERPRETER_ACTOR = name_and_ref_target(
    'file interpreter',
    'Executes a source code file using an interpreter')

ALL_ACTORS = [
    COMMAND_LINE_ACTOR,
    SOURCE_INTERPRETER_ACTOR,
    FILE_INTERPRETER_ACTOR,
]

# Bad to have definition of default value in help package.
# But do not know where the best place to put it is,
# so it remains here for some time ...
DEFAULT_ACTOR = COMMAND_LINE_ACTOR


def all_actor_cross_refs() -> list:
    return [x.cross_reference_target
            for x in ALL_ACTORS]
