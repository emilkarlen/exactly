from exactly_lib.common.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.help.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.utils import formatting
from exactly_lib.util.cli_syntax.elements.argument import Named
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs


def paths_uses_posix_syntax() -> list:
    return docs.paras("""Paths uses posix syntax.""")


def here_document_syntax_element_description(instruction_name: str,
                                             here_document_argument: Named) -> SyntaxElementDescription:
    s = _HERE_DOCUMENT_DESCRIPTION.format(instruction_name=instruction_name)
    return SyntaxElementDescription(here_document_argument.name,
                                    normalize_and_parse(s))


PATH_ARGUMENT = Named('PATH')

FILE_ARGUMENT = Named('FILE')

DIR_ARGUMENT = Named('DIR')

HERE_DOCUMENT = Named('HERE-DOCUMENT')

_HERE_DOCUMENT_DESCRIPTION = """\
A sequence of lines, given using the shell "here document" syntax.


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


def a_path_that_is_relative_the(syntax_element_name,
                                relativity_root) -> SyntaxElementDescription:
    syntax_element_name_str = syntax_element_name
    if isinstance(syntax_element_name, Named):
        syntax_element_name_str = syntax_element_name.name
    relativity_root_str = relativity_root
    if isinstance(relativity_root_str, ConceptDocumentation):
        relativity_root_str = formatting.concept(relativity_root.name().singular)
    text = 'A path that is relative to the ' + relativity_root_str + '.'
    return SyntaxElementDescription(syntax_element_name_str,
                                    docs.paras(text))
