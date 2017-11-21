from exactly_lib.common.help.see_also import SeeAlsoUrlInfo
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.util.textformat.parse import normalize_and_parse

_MAIN_DESCRIPTION_REST = """\
"""

SEE_ALSO_URL_INFO = SeeAlsoUrlInfo('Python regular expressions',
                                   'https://docs.python.org/3/library/re.html#regular-expression-syntax')

DOCUMENTATION = syntax_element_documentation(None,
                                             syntax_elements.REGEX_SYNTAX_ELEMENT,
                                             normalize_and_parse(_MAIN_DESCRIPTION_REST),
                                             [],
                                             [],
                                             [SEE_ALSO_URL_INFO])
