from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.entities.builtin import render
from exactly_lib.help.entities.builtin.contents_structure import builtin_symbols_help


def builtin_symbols_entity_configuration(all_builtin_symbols_docs: list) -> EntityTypeConfiguration:
    return EntityTypeConfiguration(builtin_symbols_help(all_builtin_symbols_docs),
                                   render.IndividualBuiltinSymbolConstructor,
                                   render.list_renderer_getter(),
                                   render.hierarchy_generator_getter())
