from exactly_lib.help.builtin import render
from exactly_lib.help.builtin.contents_structure import builtin_symbols_help
from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    entity_doc_list_renderer_as_flat_list_of_single_line_description


def builtin_symbols_entity_configuration(all_builtin_symbols_docs: list) -> EntityConfiguration:
    return EntityConfiguration(builtin_symbols_help(all_builtin_symbols_docs),
                               render.IndividualBuiltinSymbolRenderer,
                               entity_doc_list_renderer_as_flat_list_of_single_line_description)
