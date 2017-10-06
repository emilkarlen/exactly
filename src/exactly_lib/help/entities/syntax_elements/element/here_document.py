from exactly_lib.common.help.see_also import no_see_also
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help_texts.entity.syntax_element import HERE_DOCUMENT_SYNTAX_ELEMENT
from exactly_lib.util.textformat.parse import normalize_and_parse

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
"""

DOCUMENTATION = SyntaxElementDocumentation(HERE_DOCUMENT_SYNTAX_ELEMENT,
                                           normalize_and_parse(_MAIN_DESCRIPTION_REST),
                                           [],
                                           no_see_also())
