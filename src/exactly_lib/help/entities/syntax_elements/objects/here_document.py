from exactly_lib.definitions import syntax_descriptions, misc_texts
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity.types import STRING_TYPE_INFO
from exactly_lib.definitions.primitives import string
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.util.textformat.textformat_parser import TextParser

_MAIN_DESCRIPTION_REST = """\
```
{HERE_DOCUMENT_MARKER_PREFIX}{MARKER}
first line
...
last line
{MARKER}
```


Any single-word {plain_string} may be used instead of "{MARKER}" as marker.
What matters is that the maker at start and end of input
matches.


{Sym_refs_are_substituted}
"""

_TEXT_PARSER = TextParser({
    'Sym_refs_are_substituted': syntax_descriptions.symbols_are_substituted_in('the text'),
    'HERE_DOCUMENT_MARKER_PREFIX': string.HERE_DOCUMENT_MARKER_PREFIX,
    'MARKER': 'EOF',
    'plain_string': misc_texts.PLAIN_STRING,
})

DOCUMENTATION = syntax_element_documentation(None,
                                             syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT,
                                             _TEXT_PARSER.fnap(_MAIN_DESCRIPTION_REST),
                                             (),
                                             [],
                                             [],
                                             cross_reference_id_list([
                                                 STRING_TYPE_INFO,
                                                 syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
                                             ]))
