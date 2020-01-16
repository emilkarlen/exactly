from typing import List

from exactly_lib.definitions.test_suite import file_names
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments
from exactly_lib_test.test_resources.files.file_structure import File


class SuiteFileCase:
    def __init__(self,
                 suite_file_name: str,
                 suite_arguments: List[str]):
        self.suite_file_name = suite_file_name
        self.suite_arguments = suite_arguments

    def suite_file(self, contents: str) -> File:
        return File(self.suite_file_name, contents)


def suite_cases(name_of_explicit_suite_file: str) -> List[NameAndValue[SuiteFileCase]]:
    return [
        NameAndValue('explicit suite file',
                     SuiteFileCase(
                         name_of_explicit_suite_file,
                         cl_arguments.explicit_suite__part(name_of_explicit_suite_file)
                     )),

        NameAndValue('default suite file',
                     SuiteFileCase(
                         file_names.DEFAULT_SUITE_FILE,
                         []
                     )),

    ]
