from exactly_lib.help.entities.actors.actor import command_line, file_interpreter_actor, source_interpreter_actor, \
    null_actor
from exactly_lib.help_texts.entity.actors import DEFAULT_ACTOR

ALL_ACTOR_DOCS = [
    command_line.DOCUMENTATION,
    file_interpreter_actor.DOCUMENTATION,
    source_interpreter_actor.DOCUMENTATION,
    null_actor.DOCUMENTATION,
]

NAME_2_ACTOR_DOC = dict(map(lambda x: (x.singular_name(), x), ALL_ACTOR_DOCS))

DEFAULT_ACTOR_DOC = NAME_2_ACTOR_DOC[DEFAULT_ACTOR.singular_name]
