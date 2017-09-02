from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpRequestRendererResolver
from exactly_lib.help.types import render
from exactly_lib.help.utils.entity_documentation import EntitiesHelp


def type_help_request_renderer_resolver(types_help: EntitiesHelp) -> EntityHelpRequestRendererResolver:
    return EntityHelpRequestRendererResolver(render.IndividualTypeRenderer,
                                             render.all_types_list_renderer,
                                             types_help.all_entities)
