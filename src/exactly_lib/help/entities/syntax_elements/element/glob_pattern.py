from exactly_lib.common.help.see_also import no_see_also
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help_texts.entity import syntax_element
from exactly_lib.util.textformat.parse import normalize_and_parse

_MAIN_DESCRIPTION_REST = """\
"""

DOCUMENTATION = SyntaxElementDocumentation(syntax_element.GLOB_PATTERN_SYNTAX_ELEMENT,
                                           normalize_and_parse(_MAIN_DESCRIPTION_REST),
                                           [],
                                           no_see_also())
