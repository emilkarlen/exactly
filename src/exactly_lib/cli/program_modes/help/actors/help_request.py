from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpRequest, EntityHelpItem
from exactly_lib.help.actors.contents_structure import ActorDocumentation
from exactly_lib.help.entity_names import ACTOR_ENTITY_TYPE_NAME


class ActorHelpRequest(EntityHelpRequest):
    def __init__(self,
                 item: EntityHelpItem,
                 individual_actor: ActorDocumentation = None):
        super().__init__(ACTOR_ENTITY_TYPE_NAME, item, individual_actor)
