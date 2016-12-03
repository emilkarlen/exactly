from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpRequestRendererResolver
from exactly_lib.help.actors import render
from exactly_lib.help.utils.entity_documentation import EntitiesHelp


def actor_help_request_renderer_resolver(actors_help: EntitiesHelp) -> EntityHelpRequestRendererResolver:
    return EntityHelpRequestRendererResolver(render.IndividualActorRenderer,
                                             render.all_actors_list_renderer,
                                             actors_help.all_entities)
