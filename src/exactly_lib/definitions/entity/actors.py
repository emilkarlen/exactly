from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.entity.all_entity_types import ACTOR_ENTITY_TYPE_NAMES
from exactly_lib.definitions.test_case import phase_names
from . import syntax_elements


def actor_cross_ref(actor_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(ACTOR_ENTITY_TYPE_NAMES,
                                  actor_name)


def name_and_ref_target(name: str,
                        single_line_description_str: str) -> SingularNameAndCrossReferenceId:
    return SingularNameAndCrossReferenceId(name,
                                           single_line_description_str,
                                           actor_cross_ref(name))


COMMAND_LINE_ACTOR = name_and_ref_target(
    'command line',
    'Executes a command line, in terms of a {}'.format(syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name)
)

SOURCE_INTERPRETER_ACTOR = name_and_ref_target(
    'source interpreter',
    'Treats the {act_phase} phase as source code to be executed by an {interpreter}'.format(
        act_phase=phase_names.ACT.syntax,
        interpreter=syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT.singular_name,
    )
)

FILE_INTERPRETER_ACTOR = name_and_ref_target(
    'file interpreter',
    'Executes a source code file using an ' + syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT.singular_name
)

NULL_ACTOR = name_and_ref_target(
    'null',
    'Ignores the contents of the {act_phase} phase. '
    'Exit code is unconditionally 0, and there is no output on neither stdout nor stderr'.format(
        act_phase=phase_names.ACT.syntax)
)

ALL_ACTORS = [
    COMMAND_LINE_ACTOR,
    FILE_INTERPRETER_ACTOR,
    SOURCE_INTERPRETER_ACTOR,
    NULL_ACTOR,
]

DEFAULT_ACTOR = COMMAND_LINE_ACTOR

DEFAULT_ACTOR_SINGLE_LINE_VALUE = (formatting.entity(DEFAULT_ACTOR.singular_name) +
                                   ' - ' +
                                   DEFAULT_ACTOR.single_line_description_str)


def all_actor_cross_refs() -> list:
    return [x.cross_reference_target
            for x in ALL_ACTORS]
