from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.entities.types import render
from exactly_lib.help.entities.types.all_types import all_types
from exactly_lib.help.entities.types.contents_structure import types_help

TYPE_ENTITY_CONFIGURATION = EntityTypeConfiguration(
    types_help(all_types()),
    render.IndividualTypeConstructor,
    render.list_render_getter(),
    render.hierarchy_generator_getter())
