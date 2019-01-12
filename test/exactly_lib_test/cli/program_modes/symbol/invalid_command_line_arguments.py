import unittest

from exactly_lib.cli.definitions import exit_codes
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.test_resources import test_with_files_in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.test_resources.files.file_structure import empty_dir, DirContents
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

    def test_test_case_file_argument_does_not_exist(self):
        test_with_files_in_tmp_dir.check(
            self,
            symbol_args.arguments(['non-existing.case']),
            Arrangement(),
            asrt_proc_result.is_result_for_empty_stdout(
                exit_codes.EXIT_INVALID_USAGE
            )
        )

    def test_test_case_file_argument_is_a_directory(self):
        a_dir = empty_dir('a-dir')
        test_with_files_in_tmp_dir.check(
            self,
            symbol_args.arguments([a_dir.name]),
            Arrangement(
                cwd_contents=DirContents([a_dir])
            ),
            asrt_proc_result.is_result_for_empty_stdout(
                exit_codes.EXIT_INVALID_USAGE
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
