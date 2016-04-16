import os
import pathlib
import unittest

from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.cli_environment.exit_values import NO_EXECUTION_EXIT_CODE
from shellcheck_lib.cli.main_program import HELP_COMMAND
from shellcheck_lib.cli.program_modes.help import arguments_for
from shellcheck_lib.default.program_modes.test_case.default_instructions_setup import INSTRUCTIONS_SETUP
from shellcheck_lib.default.program_modes.test_suite.reporting import INVALID_SUITE_EXIT_CODE, FAILED_TESTS_EXIT_CODE
from shellcheck_lib.execution import phases
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.help.concepts.concept import SANDBOX_CONCEPT
from shellcheck_lib.help.program_modes.test_case.config import phase_help_name
from shellcheck_lib.test_case.test_case_processing import AccessErrorType
from shellcheck_lib.test_suite.parser import SECTION_NAME__SUITS, SECTION_NAME__CASES
from shellcheck_lib.util.string import lines_content
from shellcheck_lib_test.cli.test_resources.execute_main_program import execute_main_program, \
    ARGUMENTS_FOR_TEST_INTERPRETER
from shellcheck_lib_test.default.test_resources import default_main_program_case_preprocessing
from shellcheck_lib_test.default.test_resources import default_main_program_suite_preprocessing as pre_proc_tests
from shellcheck_lib_test.default.test_resources import default_main_program_wildcard as wildcard
from shellcheck_lib_test.test_resources.file_structure import DirContents, File
from shellcheck_lib_test.test_resources.file_utils import tmp_file_containing, tmp_file_containing_lines
from shellcheck_lib_test.test_resources.main_program import main_program_check_for_test_case
from shellcheck_lib_test.test_resources.main_program import main_program_check_for_test_suite
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner, \
    RunViaMainProgramInternally


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


class TestTestCasePreprocessing(main_program_check_for_test_case.TestsForSetupWithPreprocessorInternally):
    def test_transformation_into_test_case_that_pass(self):
        self._check([],
                    default_main_program_case_preprocessing.TransformationIntoTestCaseThatPass())

    def test_transformation_into_test_case_that_parser_error(self):
        self._check([],
                    default_main_program_case_preprocessing.TransformationIntoTestCaseThatParserError())


def suite_for_test_case_preprocessing(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(main_program_check_for_test_case.TestForSetupWithPreprocessor(
        default_main_program_case_preprocessing.TransformationIntoTestCaseThatPass(),
        main_program_runner))
    ret_val.addTest(main_program_check_for_test_case.TestForSetupWithPreprocessor(
        default_main_program_case_preprocessing.TransformationIntoTestCaseThatParserError(),
        main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestTestCaseWithoutInstructions))
    ret_val.addTest(unittest.makeSuite(TestTestCasePreprocessing))
    ret_val.addTest(suite_for_test_case_preprocessing(RunViaMainProgramInternally()))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
