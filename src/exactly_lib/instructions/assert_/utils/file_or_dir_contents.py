from typing import List

from exactly_lib.processing import exit_values
from exactly_lib.test_case_utils.file_properties import FileType, TYPE_INFO
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


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


_ERROR_WHEN_INVALID_FILE_DESCRIPTION = """\
The result is {HARD_ERROR} if {checked_file} is not an existing {file_type}.


Symbolic links are followed.
"""
