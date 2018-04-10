from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity.types import STRING_TYPE_INFO
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.util.textformat.textformat_parser import TextParser

_MAIN_DESCRIPTION_REST = """\
```
<<EOF
first line
...
last line
EOF
```


Any single-word string may be used instead of "EOF" as marker.
What matters is that the maker at start and end of input
matches.


Any {SYMBOL_REFERENCE_SYNTAX_ELEMENT} appearing in the text is substituted.

"""

_TEXT_PARSER = TextParser({
    'SYMBOL_REFERENCE_SYNTAX_ELEMENT': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name

})
DOCUMENTATION = syntax_element_documentation(None,
                                             syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT,
                                             _TEXT_PARSER.fnap(_MAIN_DESCRIPTION_REST),
                                             [],
                                             [],
                                             cross_reference_id_list([
                                                 STRING_TYPE_INFO,
                                                 syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
                                             ]))
