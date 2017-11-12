from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.help_texts.entity import syntax_element
from exactly_lib.util.textformat.parse import normalize_and_parse

_MAIN_DESCRIPTION_REST = """\
"""

DOCUMENTATION = syntax_element_documentation(syntax_element.GLOB_PATTERN_SYNTAX_ELEMENT,
                                             normalize_and_parse(_MAIN_DESCRIPTION_REST),
                                             [],
                                             [],
                                             [])
