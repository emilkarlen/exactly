from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.entities.syntax_elements import contents_structure, render, all_syntax_elements

SYNTAX_ELEMENT_ENTITY_CONFIGURATION = EntityTypeConfiguration(
    contents_structure.syntax_elements_help(all_syntax_elements.ALL_SYNTAX_ELEMENT_DOCS),
    render.IndividualSyntaxElementConstructor,
    render.list_render_getter(),
    render.hierarchy_generator_getter())
