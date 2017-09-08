from exactly_lib.help.concepts import render
from exactly_lib.help.concepts.all_concepts import all_concepts
from exactly_lib.help.concepts.contents_structure import concepts_help
from exactly_lib.help.contents_structure import EntityConfiguration

CONCEPT_ENTITY_CONFIGURATION = EntityConfiguration(
    concepts_help(all_concepts()),
    render.IndividualConceptRenderer,
    render.list_renderer_getter(),
    render.hierarchy_generator_getter())
