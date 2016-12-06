from exactly_lib.help.actors.actor import command_line, interpreter_actor
from exactly_lib.help.actors.names_and_cross_references import DEFAULT_ACTOR

ALL_ACTOR_DOCS = [
    command_line.DOCUMENTATION,
    interpreter_actor.DOCUMENTATION,
]

NAME_2_ACTOR_DOC = dict(map(lambda x: (x.singular_name(), x), ALL_ACTOR_DOCS))

DEFAULT_ACTOR_DOC = NAME_2_ACTOR_DOC[DEFAULT_ACTOR.singular_name]
