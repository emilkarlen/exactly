from typing import List, Sequence

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, invokation_variant_from_args
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.processing import exit_values
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher.impl import file_contents_utils, dir_contents
from exactly_lib.test_case_utils.file_matcher.impl.regular_file_contents import NAMES
from exactly_lib.test_case_utils.file_properties import FileType, TYPE_INFO
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

TRAVERSAL_OPTION_USAGES = (a.Single(a.Multiplicity.OPTIONAL, file_or_dir_contents.DIR_FILE_SET_OPTIONS),)


def description(
        checked_file: str,
        expected_file_type: FileType,
) -> List[ParagraphItem]:
    tp = TextParser({
        'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
        'checked_file': checked_file,
        'file_type': TYPE_INFO[expected_file_type].name,
        'SYMBOLIC_LINKS_ARE_FOLLOWED': misc_texts.SYMBOLIC_LINKS_ARE_FOLLOWED,
    })
    return tp.fnap(_ERROR_WHEN_INVALID_FILE_DESCRIPTION)


_TP = TextParser({
    'recursion_option': option_syntax.option_syntax(file_or_dir_contents.RECURSIVE_OPTION.name),
    'directory': file_properties.TYPE_INFO[FileType.DIRECTORY].name,
})


def get_recursion_option_description() -> List[ParagraphItem]:
    return _TP.fnap(DIR_CONTENTS_RECURSION_DESCRIPTION)


def get_dir_syntax_descriptions() -> Sequence[SyntaxElementDescription]:
    return [
        get_traversal_options_sed()
    ]


def get_traversal_options_sed() -> SyntaxElementDescription:
    return SyntaxElementDescription(
        file_or_dir_contents.DIR_FILE_SET_OPTIONS.name,
        _TP.fnap(_DIR_FILE_SET_OPTIONS_MAIN),
        [
            invokation_variant_from_args([
                a.Single(
                    a.Multiplicity.MANDATORY,
                    file_or_dir_contents.RECURSIVE_OPTION
                ),
                a.Single(
                    a.Multiplicity.OPTIONAL,
                    file_or_dir_contents.MIN_DEPTH_OPTION,
                ),
                a.Single(
                    a.Multiplicity.OPTIONAL,
                    file_or_dir_contents.MAX_DEPTH_OPTION,
                ),
            ],
                _TP.fnap(DIR_CONTENTS_RECURSION_DESCRIPTION),
            )
        ]
    )


REGULAR_FILE_DOCUMENTATION_SETUP = file_contents_utils.DocumentationSetup(
    NAMES,
    ()
)

DIR_DOCUMENTATION = file_contents_utils.DocumentationSetup(
    dir_contents.NAMES,
    TRAVERSAL_OPTION_USAGES,
    get_dir_syntax_descriptions,
)

_ERROR_WHEN_INVALID_FILE_DESCRIPTION = """\
The result is {HARD_ERROR} if {checked_file} is not an existing {file_type}.

{SYMBOLIC_LINKS_ARE_FOLLOWED}.
"""

MATCHER_FILE_HANDLING_DESCRIPTION = file_contents_utils.MATCHER_FILE_HANDLING_DESCRIPTION

_DIR_FILE_SET_OPTIONS_MAIN = """\
By default, only the direct contents of the tested directory is included -
sub directory contents is excluded.
"""

DIR_CONTENTS_RECURSION_DESCRIPTION = """\
Includes sub directory contents (recursively).


Sub directory contents may be limited by specifying
limits for the depth.


Depth 0 is the direct contents of the tested directory. 
"""
