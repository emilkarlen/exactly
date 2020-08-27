from exactly_lib.definitions import syntax_descriptions
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.util.textformat.parse import normalize_and_parse

_MAIN_DESCRIPTION_REST = syntax_descriptions.SYMBOL_NAME_SYNTAX_DESCRIPTION

DOCUMENTATION = syntax_element_documentation(None,
                                             syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
                                             normalize_and_parse(_MAIN_DESCRIPTION_REST),
                                             (),
                                             [],
                                             [],
                                             [concepts.SYMBOL_CONCEPT_INFO.cross_reference_target])
