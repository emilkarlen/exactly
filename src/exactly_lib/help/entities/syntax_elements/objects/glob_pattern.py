from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.util.textformat.parse import normalize_and_parse

_MAIN_DESCRIPTION_REST = """\
"""

DOCUMENTATION = syntax_element_documentation(None,
                                             syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT,
                                             normalize_and_parse(_MAIN_DESCRIPTION_REST),
                                             [],
                                             [],
                                             [])
