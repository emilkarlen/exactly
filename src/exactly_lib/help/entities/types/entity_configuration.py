from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.entities.types import render
from exactly_lib.help.entities.types.all_types import all_types
from exactly_lib.help.entities.types.contents_structure import types_help

TYPE_ENTITY_CONFIGURATION = EntityConfiguration(
    types_help(all_types()),
    render.IndividualTypeRenderer,
    render.list_render_getter(),
    render.hierarchy_generator_getter())
