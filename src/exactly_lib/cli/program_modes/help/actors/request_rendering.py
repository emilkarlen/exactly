from exactly_lib.cli.program_modes.help.actors.help_request import ActorHelpRequest
from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpItem
from exactly_lib.help.actors.contents_structure import ActorsHelp
from exactly_lib.help.utils.render import SectionContentsRenderer


class ActorHelpRequestRendererResolver:
    def __init__(self, actors_help: ActorsHelp):
        self.actors_help = actors_help

    def renderer_for(self, request: ActorHelpRequest) -> SectionContentsRenderer:
        from exactly_lib.help.actors import render
        item = request.item
        if item is EntityHelpItem.ALL_ENTITIES_LIST:
            return render.all_actors_list_renderer(self.actors_help)
        if item is EntityHelpItem.INDIVIDUAL_ENTITY:
            return render.IndividualActorRenderer(request.individual_actor)
        raise ValueError('Invalid %s: %s' % (str(EntityHelpItem), str(item)))
