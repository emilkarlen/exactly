from exactly_lib.help.contents_structure import EntityConfiguration
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import FlatEntityListHierarchyGeneratorGetter
from exactly_lib.help.syntax_elements import all_syntax_elements, render, contents_structure
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    FlatListRendererWithSingleLineDescriptionGetter

SYNTAX_ELEMENT_ENTITY_CONFIGURATION = EntityConfiguration(
    contents_structure.syntax_elements_help(all_syntax_elements.ALL_SYNTAX_ELEMENT_DOCS),
    render.IndividualSyntaxElementRenderer,
    FlatListRendererWithSingleLineDescriptionGetter(),
    FlatEntityListHierarchyGeneratorGetter(
        render.IndividualSyntaxElementRenderer))
