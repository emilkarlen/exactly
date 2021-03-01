from typing import Sequence

from exactly_lib.common.help import documentation_text
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, SyntaxElementDescription
from exactly_lib.definitions import formatting, logic, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.files_condition import syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class ConstantSyntaxDescription(grammar.PrimitiveDescriptionWithSyntaxElementAsInitialSyntaxToken):
    def __init__(self):
        super().__init__(_CONSTANT_SYNTAX_ELEMENT_NAME)

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return ()

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return ()

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return (
            _constant_sed(_CONSTANT_SYNTAX_ELEMENT_NAME),
            _file_condition_sed(),
            _file_name_sed(),
        )

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT,
            syntax_elements.STRING_SYNTAX_ELEMENT,
        ])


def _constant_sed(name: str) -> SyntaxElementDescription:
    return SyntaxElementDescription(
        name,
        _TP.fnap(_CONSTANT__HEADER),
        [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY, a.Constant(syntax.BEGIN_BRACE)),
                a.Single(a.Multiplicity.ONE_OR_MORE, a.Named(_FILE_CONDITION)),
                a.Single(a.Multiplicity.MANDATORY, a.Constant(syntax.END_BRACE)),
            ],
                _TP.fnap(_CONSTANT__DESCRIPTION_REST)),
        ]
    )


_CONSTANT_SYNTAX_ELEMENT_NAME = 'CONSTANT'
_FILE_CONDITION = 'FILE-CONDITION'

_CONSTANT__HEADER = """\
A sequence of file names. Each together with an optional {FILE_MATCHER}.
"""

_CONSTANT__DESCRIPTION_REST = """\
There can be only one {FILE_CONDITION} per line.


{SPACE_SEPARATION_PARAGRAPH} 
"""

_FILE_CONDITION_DESCRIPTION_REST = """\
A condition of existence of a file with a given name.
"""

_FILE_NAME_WITH_MATCHER_DESCRIPTION_REST = """\
A condition that includes matching of the named file by {FILE_MATCHER}.


Multiple {FILE_MATCHER}s may be associated with a single file name
(via multiple {FILE_CONDITION}s).

In this case, the matchers are combined using {CONJUNCTION}, in order of appearance. 


The {FILE_MATCHER_SEPARATOR} before {FILE_MATCHER}
must appear on the same line as the file name.


{SPACE_SEPARATION_PARAGRAPH} 
"""

_FILE_NAME_DESCRIPTION_REST = """\
A relative path, using {posix_syntax}.
"""

_SPACE_SEPARATION_PARAGRAPH = 'All parts must be separated by {whitespace}.'

_TP = TextParser({
    'FILE_MATCHER': syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
    'FILE_NAME': syntax.FILE_NAME.name,
    'FILE_CONDITION': _FILE_CONDITION,
    'STRING': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
    'FILE_MATCHER_SEPARATOR': formatting.keyword(syntax.FILE_MATCHER_SEPARATOR),
    'posix_syntax': documentation_text.POSIX_SYNTAX,
    'CONJUNCTION': logic.AND_OPERATOR_NAME,
    'SPACE_SEPARATION_PARAGRAPH': _SPACE_SEPARATION_PARAGRAPH.format(whitespace=misc_texts.WHITESPACE),
})


def _file_condition_sed() -> SyntaxElementDescription:
    return SyntaxElementDescription(
        _FILE_CONDITION,
        _TP.fnap(_FILE_CONDITION_DESCRIPTION_REST),
        [
            invokation_variant_from_args([
                syntax.FILE_NAME__ARG,
            ]),
            invokation_variant_from_args([
                syntax.FILE_NAME__ARG,
                a.Single(a.Multiplicity.MANDATORY, a.Constant(syntax.FILE_MATCHER_SEPARATOR)),
                syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.single_mandatory,
            ],
                _TP.fnap(_FILE_NAME_WITH_MATCHER_DESCRIPTION_REST)),
        ]
    )


def _file_name_sed() -> SyntaxElementDescription:
    return SyntaxElementDescription(
        syntax.FILE_NAME.name,
        (),
        [invokation_variant_from_args([syntax_elements.STRING_SYNTAX_ELEMENT.single_mandatory])],
        _TP.fnap(_FILE_NAME_DESCRIPTION_REST),
    )
