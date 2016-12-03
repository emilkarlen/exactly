from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpRequestRendererResolver
from exactly_lib.help.actors import render
from exactly_lib.help.actors.contents_structure import ActorsHelp


def actor_help_request_renderer_resolver(actors_help: ActorsHelp) -> EntityHelpRequestRendererResolver:
    return EntityHelpRequestRendererResolver(render.IndividualActorRenderer,
                                             render.all_actors_list_renderer,
                                             actors_help.all_actors)
