from exactly_lib.definitions.entity.all_entity_types import ACTOR_ENTITY_TYPE_NAMES
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.entities.actors.all_actor_docs import ALL_ACTOR_DOCS
from exactly_lib.help.entities.actors.contents_structure import actors_help
from exactly_lib.help.entities.actors.render import IndividualActorConstructor
from exactly_lib.help.render.entities_list_renderer import FlatEntityListHierarchyGeneratorGetter
from exactly_lib.help.render.entity_docs import \
    FlatListConstructorWithSingleLineDescriptionGetter

ACTOR_ENTITY_CONFIGURATION = EntityTypeConfiguration(
    actors_help(ALL_ACTOR_DOCS),
    IndividualActorConstructor,
    FlatListConstructorWithSingleLineDescriptionGetter(),
    FlatEntityListHierarchyGeneratorGetter(ACTOR_ENTITY_TYPE_NAMES.identifier,
                                           IndividualActorConstructor))
