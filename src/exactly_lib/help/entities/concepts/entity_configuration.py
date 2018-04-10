from exactly_lib.definitions.entity.all_entity_types import CONCEPT_ENTITY_TYPE_NAMES
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.entities.concepts import render
from exactly_lib.help.entities.concepts.all_concepts import all_concepts
from exactly_lib.help.entities.concepts.contents_structure import concepts_help
from exactly_lib.help.render.entities_list_renderer import FlatEntityListHierarchyGeneratorGetter
from exactly_lib.help.render.entity_docs import \
    FlatListConstructorWithSingleLineDescriptionGetter

CONCEPT_ENTITY_CONFIGURATION = EntityTypeConfiguration(
    concepts_help(all_concepts()),
    render.IndividualConceptConstructor,
    FlatListConstructorWithSingleLineDescriptionGetter(),
    FlatEntityListHierarchyGeneratorGetter(CONCEPT_ENTITY_TYPE_NAMES.identifier,
                                           render.IndividualConceptConstructor),
)
