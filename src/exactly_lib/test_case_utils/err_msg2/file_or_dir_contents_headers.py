from typing import Any

from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util import strings
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile


def unexpected_of_file_type(file_type: FileType) -> Any:
    return _unexpected(file_properties.TYPE_INFO[file_type].description)


def unexpected_of_std_file(file: ProcOutputFile) -> Any:
    return _unexpected(process_output_files.PROC_OUTPUT_FILE_NAMES[file])


def _unexpected(target: str) -> Any:
    return strings.FormatPositional(
        'Unexpected {} of {}',
        file_check_properties.CONTENTS,
        target,
    )
