from exactly_lib.common.help import documentation_text
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, SyntaxElementDescription
from exactly_lib.definitions import formatting, logic
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.test_case_utils.files_condition import syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

_FILE_CONDITION = 'FILE-CONDITION'

_MAIN_DESCRIPTION_REST = """\
A file name may be repeated.

If there are multiple {FILE_MATCHER}s associated with a file name,
they are combined using {CONJUNCTION}, in order of appearance. 


There can be only one {FILE_CONDITION} per line.

All parts must be separated by space.
"""

_FILE_CONDITION_DESCRIPTION_REST = """\
A condition of existence of a file with a given name.

If a {FILE_MATCHER} is given,
the condition includes matching by that matcher.


The {FILES_CONDITION_SYNTAX_ELEMENT} before the {FILE_MATCHER}
must appear on the same line as the file name.
"""

_FILE_NAME_DESCRIPTION_REST = """\
A {FILE_NAME} is a {STRING}, and use {posix_syntax}.


File names must be relative.
"""

_TP = TextParser({
    'FILE_MATCHER': syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
    'FILE_NAME': syntax.FILE_NAME,
    'FILE_CONDITION': _FILE_CONDITION,
    'STRING': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
    'FILES_CONDITION_SYNTAX_ELEMENT': formatting.keyword(syntax.FILE_MATCHER_SEPARATOR),
    'posix_syntax': documentation_text.POSIX_SYNTAX,
    'CONJUNCTION': logic.AND_OPERATOR_NAME,
})

_FILE_NAME = a.Single(a.Multiplicity.MANDATORY, a.Named(syntax.FILE_NAME))

DOCUMENTATION = syntax_element_documentation(
    None,
    syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT,
    _TP.fnap(_MAIN_DESCRIPTION_REST),
    [
        invokation_variant_from_args([
            a.Single(a.Multiplicity.MANDATORY, a.Constant(syntax.BEGIN_BRACE)),
            a.Single(a.Multiplicity.ONE_OR_MORE, a.Named(_FILE_CONDITION)),
            a.Single(a.Multiplicity.MANDATORY, a.Constant(syntax.END_BRACE)),
        ]),
    ],
    [
        SyntaxElementDescription(
            _FILE_CONDITION,
            _TP.fnap(_FILE_CONDITION_DESCRIPTION_REST),
            [
                invokation_variant_from_args([
                    _FILE_NAME,
                ]),
                invokation_variant_from_args([
                    _FILE_NAME,
                    a.Single(a.Multiplicity.MANDATORY, a.Constant(syntax.FILE_MATCHER_SEPARATOR)),
                    syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.single_mandatory,
                ]),
            ]
        ),
        SyntaxElementDescription(
            syntax.FILE_NAME,
            _TP.fnap(_FILE_NAME_DESCRIPTION_REST),
            []
        ),
    ],
    [
        syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.cross_reference_target,
        syntax_elements.STRING_SYNTAX_ELEMENT.cross_reference_target,
    ],
)
