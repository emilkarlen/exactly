from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.help_texts.entity.syntax_element import HERE_DOCUMENT_SYNTAX_ELEMENT
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse


def here_document_syntax_element_description(instruction_name: str,
                                             here_document_argument: a.Named) -> SyntaxElementDescription:
    s = _HERE_DOCUMENT_DESCRIPTION.format(
        instruction_name=instruction_name,
        single_line_description=HERE_DOCUMENT_SYNTAX_ELEMENT.single_line_description_str)
    return SyntaxElementDescription(here_document_argument.name,
                                    normalize_and_parse(s))


_HERE_DOCUMENT_DESCRIPTION = """\
{single_line_description}.


```
{instruction_name} ... <<EOF
<first line>
...
<last line>
EOF
```


Any single-word string may be used instead of "EOF" as marker.
What matters is that the maker at start and end of input
matches.
"""
