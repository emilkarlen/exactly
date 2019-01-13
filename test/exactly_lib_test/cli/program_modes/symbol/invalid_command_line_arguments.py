import unittest

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.processing import exit_values
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.test_resources import test_with_files_in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.test_resources.files.file_structure import empty_dir, DirContents
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestInvalidFileArguments)


class TestInvalidFileArguments(unittest.TestCase):
    def test_missing_test_case_file_argument(self):
        test_with_files_in_tmp_dir.check(
            self,
            symbol_args.arguments([]),
            Arrangement(),
            asrt_proc_result.is_result_for_empty_stdout(
                exit_codes.EXIT_INVALID_USAGE
            )
        )

    def test_invalid_case_file(self):
        case_file_arg = 'test.case'

        cases = [
            NEA('file does not exist',
                expected=
                asrt_proc_result.is_result_for_empty_stdout(exit_codes.EXIT_INVALID_USAGE),
                actual=
                DirContents([])
                ),
            NEA('file is a directory',
                expected=
                asrt_proc_result.is_result_for_failure_exit_value_on_stderr(
                    exit_values.NO_EXECUTION__FILE_ACCESS_ERROR
                ),
                actual=
                DirContents([
                    empty_dir(case_file_arg)
                ])
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                test_with_files_in_tmp_dir.check(
                    self,
                    command_line_arguments=
                    symbol_args.arguments([case_file_arg]),
                    arrangement=
                    Arrangement(
                        cwd_contents=case.actual
                    ),
                    expectation=
                    case.expected)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
