from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.help_texts.test_case.instructions import define_symbol
from exactly_lib.util.textformat.parse import normalize_and_parse

_MAIN_DESCRIPTION_REST = define_symbol.SYMBOL_NAME_SYNTAX_DESCRIPTION

DOCUMENTATION = syntax_element_documentation(None,
                                             syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
                                             normalize_and_parse(_MAIN_DESCRIPTION_REST),
                                             [],
                                             [],
                                             [concepts.SYMBOL_CONCEPT_INFO.cross_reference_target])
