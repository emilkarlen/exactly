from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, InvokationVariant
from exactly_lib.definitions import syntax_descriptions, misc_texts
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.definitions.primitives import string
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser
from ..common import string as string_common

_DESCRIPTION__STRING = """\
A normal {string_type}.
"""

_HERE_DOC_SYNTAX_MARKER = 'MARKER'
_HERE_DOC_LINE = 'LINE'

_DESCRIPTION__HERE_DOC = """\
A sequence of lines, resembling shell "here document" syntax.


```
{HERE_DOCUMENT_MARKER_PREFIX}{EXAMPLE_MARKER}
first line
...
last line
{EXAMPLE_MARKER}
```


Any single-word {plain_string} may be used as {MARKER},
as "{EXAMPLE_MARKER}" in the example.
What matters is that {MARKER} at the start and end of the input matches.


Each {LINE} must end with new-line.


{Sym_refs_are_substituted}
"""

_TEXT_PARSER = TextParser({
    'Sym_refs_are_substituted': syntax_descriptions.symbols_are_substituted_in('the text'),
    'HERE_DOCUMENT_MARKER_PREFIX': string.HERE_DOCUMENT_MARKER_PREFIX,
    'EXAMPLE_MARKER': 'EOF',
    'MARKER': _HERE_DOC_SYNTAX_MARKER,
    'LINE': _HERE_DOC_LINE,
    'plain_string': misc_texts.PLAIN_STRING,
    'string_type': types.STRING_TYPE_INFO.name,
})


def _normal_string() -> InvokationVariant:
    return invokation_variant_from_args(
        [syntax_elements.STRING_SYNTAX_ELEMENT.single_mandatory],
        _TEXT_PARSER.fnap(_DESCRIPTION__STRING)
    )


def _here_doc() -> InvokationVariant:
    return invokation_variant_from_args(
        [
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(string.HERE_DOCUMENT_MARKER_PREFIX + _HERE_DOC_SYNTAX_MARKER)),
            a.Single(a.Multiplicity.ZERO_OR_MORE,
                     a.Named(_HERE_DOC_LINE)),
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(_HERE_DOC_SYNTAX_MARKER)),
        ],
        _TEXT_PARSER.fnap(_DESCRIPTION__HERE_DOC)
    )


DOCUMENTATION = syntax_element_documentation(
    None,
    syntax_elements.RICH_STRING_SYNTAX_ELEMENT,
    (),
    (),
    [
        _normal_string(),
        string_common.text_until_end_of_line(),
        _here_doc(),
    ],
    [],
    cross_reference_id_list([
        types.STRING_TYPE_INFO,
        syntax_elements.STRING_SYNTAX_ELEMENT,
        syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
    ]),
)
