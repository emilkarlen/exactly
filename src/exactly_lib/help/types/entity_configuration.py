from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.types.all_types import all_types
from exactly_lib.help.types.contents_structure import types_help
from exactly_lib.help.types.render import IndividualTypeRenderer, TypesListRenderer

TYPE_ENTITY_CONFIGURATION = EntityConfiguration(types_help(all_types()),
                                                IndividualTypeRenderer,
                                                TypesListRenderer)
