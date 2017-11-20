from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.help_texts.entity import syntax_element, concepts
from exactly_lib.help_texts.name_and_cross_ref import cross_reference_id_list
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.textformat.parse import normalize_and_parse

_MAIN_DESCRIPTION_REST = symbol_reference_syntax_for_name(syntax_element.SYMBOL_NAME_SYNTAX_ELEMENT.argument.name)

DOCUMENTATION = syntax_element_documentation(None,
                                             syntax_element.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
                                             normalize_and_parse(_MAIN_DESCRIPTION_REST),
                                             [],
                                             [],
                                             cross_reference_id_list([
                                                 concepts.SYMBOL_CONCEPT_INFO,
                                                 syntax_element.SYMBOL_NAME_SYNTAX_ELEMENT,
                                             ]))
