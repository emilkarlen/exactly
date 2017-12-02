from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.entities.concepts import render
from exactly_lib.help.entities.concepts.all_concepts import all_concepts
from exactly_lib.help.entities.concepts.contents_structure import concepts_help
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import FlatEntityListHierarchyGeneratorGetter
from exactly_lib.help.utils.rendering.entity_docs import \
    FlatListConstructorWithSingleLineDescriptionGetter
from exactly_lib.help_texts.entity.all_entity_types import CONCEPT_ENTITY_TYPE_NAMES

CONCEPT_ENTITY_CONFIGURATION = EntityConfiguration(
    concepts_help(all_concepts()),
    render.IndividualConceptConstructor,
    FlatListConstructorWithSingleLineDescriptionGetter(),
    FlatEntityListHierarchyGeneratorGetter(CONCEPT_ENTITY_TYPE_NAMES.identifier,
                                           render.IndividualConceptConstructor),
)
