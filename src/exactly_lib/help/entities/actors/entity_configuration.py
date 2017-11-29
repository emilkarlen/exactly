from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.entities.actors.all_actor_docs import ALL_ACTOR_DOCS
from exactly_lib.help.entities.actors.contents_structure import actors_help
from exactly_lib.help.entities.actors.render import IndividualActorRenderer
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import FlatEntityListHierarchyGeneratorGetter
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    FlatListRendererWithSingleLineDescriptionGetter
from exactly_lib.help_texts.entity.all_entity_types import ACTOR_ENTITY_TYPE_NAMES

ACTOR_ENTITY_CONFIGURATION = EntityConfiguration(
    actors_help(ALL_ACTOR_DOCS),
    IndividualActorRenderer,
    FlatListRendererWithSingleLineDescriptionGetter(),
    FlatEntityListHierarchyGeneratorGetter(ACTOR_ENTITY_TYPE_NAMES.identifier,
                                           IndividualActorRenderer))
