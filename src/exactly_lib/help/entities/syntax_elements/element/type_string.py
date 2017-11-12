from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help_texts.entity import syntax_element
from exactly_lib.util.textformat.parse import normalize_and_parse

_MAIN_DESCRIPTION_REST = """\
"""

DOCUMENTATION = SyntaxElementDocumentation(syntax_element.STRING_SYNTAX_ELEMENT,
                                           normalize_and_parse(_MAIN_DESCRIPTION_REST),
                                           [],
                                           [])
