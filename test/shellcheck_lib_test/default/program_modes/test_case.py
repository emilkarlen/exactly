import os
import unittest

from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.cli_environment.exit_values import NO_EXECUTION_EXIT_CODE
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.test_case_processing import AccessErrorType
from shellcheck_lib_test.cli.test_resources.execute_main_program import execute_main_program, \
    ARGUMENTS_FOR_TEST_INTERPRETER
from shellcheck_lib_test.default.test_resources import default_main_program_case_preprocessing
from shellcheck_lib_test.test_resources.file_utils import tmp_file_containing, tmp_file_containing_lines
from shellcheck_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_with_preprocessor
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.main_program.main_program_runners import RunViaMainProgramInternally


class TestTestCaseWithoutInstructions(unittest.TestCase):
    def test_invalid_usage(self):
        # ARRANGE #
        test_case_source = ''
        with tmp_file_containing(test_case_source) as file_path:
            argv = ['--invalid-option-that-should-cause-failure', str(file_path)]
            # ACT #
            sub_process_result = execute_main_program(argv)
        # ASSERT #
        self.assertEqual(main_program.EXIT_INVALID_USAGE,
                         sub_process_result.exitcode,
                         'Exit Status')
        self.assertEqual('',
                         sub_process_result.stdout,
                         'Output on stdout')
        self.assertTrue(len(sub_process_result.stderr) > 0,
                        'An error message should be printed on stderr')

    def test_empty_file(self):
        # ARRANGE #
        test_case_source = ''
        with tmp_file_containing(test_case_source) as file_path:
            argv = ARGUMENTS_FOR_TEST_INTERPRETER + [str(file_path)]
            # ACT #
            sub_process_result = execute_main_program(argv)
        # ASSERT #
        self.assertEqual(0,
                         sub_process_result.exitcode,
                         'Exit Status')
        self.assertEqual(FullResultStatus.PASS.name + os.linesep,
                         sub_process_result.stdout,
                         'Output on stdout')

    def test_empty_phases(self):
        # ARRANGE #
        test_case_lines = [
            '[setup]',
            '[act]',
            '[assert]',
            '[cleanup]',
        ]
        with tmp_file_containing_lines(test_case_lines) as file_path:
            argv = ARGUMENTS_FOR_TEST_INTERPRETER + [str(file_path)]
            # ACT #
            sub_process_result = execute_main_program(argv)
        # ASSERT #
        self.assertEqual(0,
                         sub_process_result.exitcode,
                         'Exit Status')
        self.assertEqual(FullResultStatus.PASS.name + os.linesep,
                         sub_process_result.stdout,
                         'Output on stdout')

    def test_parse_error(self):
        # ARRANGE #
        test_case_lines = [
            '[invalid phase]',
        ]
        with tmp_file_containing_lines(test_case_lines) as file_path:
            argv = ARGUMENTS_FOR_TEST_INTERPRETER + [str(file_path)]
            # ACT #
            sub_process_result = execute_main_program(argv)
        # ASSERT #
        self.assertEqual(sub_process_result.exitcode,
                         NO_EXECUTION_EXIT_CODE,
                         'Exit Status')
        self.assertEqual(AccessErrorType.PARSE_ERROR.name + os.linesep,
                         sub_process_result.stdout,
                         'Output on stdout')


def suite_for_test_case_preprocessing(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return tests_for_setup_with_preprocessor(
        [
            default_main_program_case_preprocessing.TransformationIntoTestCaseThatPass(),
            default_main_program_case_preprocessing.TransformationIntoTestCaseThatParserError(),
        ],
        main_program_runner)


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestTestCaseWithoutInstructions))
    ret_val.addTest(suite_for_test_case_preprocessing(RunViaMainProgramInternally()))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
