from enum import Enum

from exactly_lib.cli.program_modes.help.program_modes.help_request import HelpRequest
from exactly_lib.help.actors.contents_structure import ActorDocumentation


class ActorHelpItem(Enum):
    ALL_ACTORS_LIST = 0
    INDIVIDUAL_ACTOR = 1


class ActorHelpRequest(HelpRequest):
    def __init__(self,
                 item: ActorHelpItem,
                 individual_actor: ActorDocumentation = None):
        self._item = item
        self._individual_actor = individual_actor

    @property
    def item(self) -> ActorHelpItem:
        return self._item

    @property
    def individual_actor(self) -> ActorDocumentation:
        return self._individual_actor
