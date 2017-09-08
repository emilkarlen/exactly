from exactly_lib.help.actors.all_actor_docs import ALL_ACTOR_DOCS
from exactly_lib.help.actors.contents_structure import actors_help
from exactly_lib.help.actors.render import IndividualActorRenderer
from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    entity_doc_list_renderer_as_flat_list_of_single_line_description

ACTOR_ENTITY_CONFIGURATION = EntityConfiguration(actors_help(ALL_ACTOR_DOCS),
                                                 IndividualActorRenderer,
                                                 entity_doc_list_renderer_as_flat_list_of_single_line_description)
