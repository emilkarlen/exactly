from exactly_lib.help.builtin import render
from exactly_lib.help.builtin.contents_structure import builtin_symbols_help
from exactly_lib.help.contents_structure import EntityConfiguration


def builtin_symbols_entity_configuration(all_builtin_symbols_docs: list) -> EntityConfiguration:
    return EntityConfiguration(builtin_symbols_help(all_builtin_symbols_docs),
                               render.IndividualBuiltinSymbolRenderer,
                               render.list_renderer_getter(),
                               render.hierarchy_generator_getter())
