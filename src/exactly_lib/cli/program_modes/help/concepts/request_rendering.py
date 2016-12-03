from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpRequestRendererResolver
from exactly_lib.help.concepts import render
from exactly_lib.help.concepts.contents_structure import ConceptsHelp


def concept_help_request_renderer_resolver(concepts_help: ConceptsHelp) -> EntityHelpRequestRendererResolver:
    return EntityHelpRequestRendererResolver(render.IndividualConceptRenderer,
                                             render.all_concepts_list_renderer,
                                             concepts_help.all_concepts)
