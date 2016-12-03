from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpRequest, EntityHelpItem
from exactly_lib.help.actors.contents_structure import ActorDocumentation


class ActorHelpRequest(EntityHelpRequest):
    def __init__(self,
                 item: EntityHelpItem,
                 individual_actor: ActorDocumentation = None):
        super().__init__(item)
        self._item = item
        self._individual_actor = individual_actor

    @property
    def individual_actor(self) -> ActorDocumentation:
        return self._individual_actor
