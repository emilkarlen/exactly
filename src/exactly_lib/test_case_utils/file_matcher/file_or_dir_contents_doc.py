from typing import List

from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.processing import exit_values
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType, TYPE_INFO
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

RECURSION_OPTIONS = (a.Single(a.Multiplicity.OPTIONAL, file_or_dir_contents.RECURSIVE_OPTION),)


def description(
        checked_file: str,
        expected_file_type: FileType,
) -> List[ParagraphItem]:
    tp = TextParser({
        'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
        'checked_file': checked_file,
        'file_type': TYPE_INFO[expected_file_type].name
    })
    return tp.fnap(_ERROR_WHEN_INVALID_FILE_DESCRIPTION)


def get_recursion_option_description() -> List[ParagraphItem]:
    tp = TextParser({
        'recursion_option': option_syntax.option_syntax(file_or_dir_contents.RECURSIVE_OPTION.name),
        'directory': file_properties.TYPE_INFO[FileType.DIRECTORY].name,
    })

    return tp.fnap(DIR_CONTENTS_RECURSION_DESCRIPTION)


_ERROR_WHEN_INVALID_FILE_DESCRIPTION = """\
The result is {HARD_ERROR} if {checked_file} is not an existing {file_type}.

Symbolic links are followed.
"""

MATCHER_FILE_HANDLING_DESCRIPTION = """\
The result is {HARD_ERROR} for {MODEL:a} that is not {_file_type_:a}.

Symbolic links are followed.
"""

DIR_CONTENTS_RECURSION_DESCRIPTION = """\
If the {recursion_option} option is given,
the contents of sub directories is included (recursively).

Otherwise, sub {directory} contents is excluded. 
"""
