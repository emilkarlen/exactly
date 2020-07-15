import unittest

from exactly_lib.processing import exit_values
from exactly_lib_test.cli.program_modes.test_resources import test_with_files_in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.cli.test_resources import cli_arguments
from exactly_lib_test.processing.test_resources import preprocessor_utils
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestInvalidPreprocessor)


class TestInvalidPreprocessor(unittest.TestCase):
    def test_preprocessor_that_fails_with_no_output(self):
        valid_successful_case = File.empty('valid.case')
        py_pgm_that_fails_unconditionally = File(
            'preprocessor.py',
            preprocessor_utils.PREPROCESSOR_THAT_FAILS_UNCONDITIONALLY__PY_SRC
        )

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            cli_arguments.py_preprocessing_and_case(py_pgm_that_fails_unconditionally.name,
                                                    valid_successful_case.name),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    py_pgm_that_fails_unconditionally,
                    valid_successful_case,
                ])
            ),
            expectation=
            asrt_proc_result.is_result_for_exit_value(
                exit_values.NO_EXECUTION__PRE_PROCESS_ERROR
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
