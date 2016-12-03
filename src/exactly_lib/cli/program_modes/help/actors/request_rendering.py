from exactly_lib.cli.program_modes.help.actors.help_request import ActorHelpRequest, ActorHelpItem
from exactly_lib.help.actors.contents_structure import ActorsHelp
from exactly_lib.help.utils.render import SectionContentsRenderer


class ActorHelpRequestRendererResolver:
    def __init__(self, actors_help: ActorsHelp):
        self.actors_help = actors_help

    def renderer_for(self, request: ActorHelpRequest) -> SectionContentsRenderer:
        from exactly_lib.help.actors import render
        item = request.item
        if item is ActorHelpItem.ALL_ACTORS_LIST:
            return render.all_actors_list_renderer(self.actors_help)
        if item is ActorHelpItem.INDIVIDUAL_ACTOR:
            return render.IndividualActorRenderer(request.individual_actor)
        raise ValueError('Invalid %s: %s' % (str(ActorHelpItem), str(item)))
