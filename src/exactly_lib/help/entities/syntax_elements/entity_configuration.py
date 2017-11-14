from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.entities.syntax_elements import contents_structure, render, all_syntax_elements

SYNTAX_ELEMENT_ENTITY_CONFIGURATION = EntityConfiguration(
    contents_structure.syntax_elements_help(all_syntax_elements.ALL_SYNTAX_ELEMENT_DOCS),
    render.IndividualSyntaxElementRenderer,
    render.list_render_getter(),
    render.hierarchy_generator_getter())
