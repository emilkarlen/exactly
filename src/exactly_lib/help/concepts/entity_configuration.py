from exactly_lib.help.concepts.all_concepts import all_concepts
from exactly_lib.help.concepts.contents_structure import concepts_help
from exactly_lib.help.concepts.render import IndividualConceptRenderer, all_concepts_list_renderer
from exactly_lib.help.contents_structure import EntityConfiguration

CONCEPT_ENTITY_CONFIGURATION = EntityConfiguration(concepts_help(all_concepts()),
                                                   IndividualConceptRenderer,
                                                   all_concepts_list_renderer)
