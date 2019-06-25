import unittest

from exactly_lib.processing import exit_values
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.test_resources import test_with_files_in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFailingScenarios)


class TestFailingScenarios(unittest.TestCase):

    def test_invalid_type_of_file_arguments(self):
        # ARRANGE #
        a_dir = empty_dir('a-dir')
        test_with_files_in_tmp_dir.check(
            self,
            symbol_args.arguments([a_dir.name]),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([a_dir])
            ),
            expectation=
            asrt_proc_result.is_result_for_exit_value_on_stderr_and_empty_stdout(
                exit_values.NO_EXECUTION__FILE_ACCESS_ERROR
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
