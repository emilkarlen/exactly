import io
import os
import unittest

from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.general.output import StdOutputFiles
from shellcheck_lib_test.util.with_tmp_file import tmp_file_containing, tmp_file_containing_lines
from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.default import default_main_program as sut
from shellcheck_lib.cli.execution_mode.test_case.instruction_setup import InstructionsSetup


def name_argument_splitter(s: str) -> (str, str):
    return s[0], s[1:]


instructions_setup = InstructionsSetup(
    {},
    {},
    {},
    {})


def execute_main_program(arguments: list):
    stdout_file = io.StringIO()
    stderr_file = io.StringIO()
    program = sut.MainProgram(StdOutputFiles(stdout_file, stderr_file),
                              name_argument_splitter,
                              instructions_setup)
    exit_status = program.execute(arguments)
    stdout_contents = stdout_file.getvalue()
    stdout_file.close()
    stderr_contents = stderr_file.getvalue()
    stderr_file.close()
    return exit_status, stdout_contents, stderr_contents


class TestTestCaseWithoutInstructions(unittest.TestCase):
    def test_invalid_usage(self):
        # ARRANGE #
        test_case_source = ''
        with tmp_file_containing(test_case_source) as file_path:
            argv = ['--invalid-option-that-should-cause-failure', str(file_path)]
            # ACT #
            exit_status, stdout_contents, stderr_contents = execute_main_program(argv)
        # ASSERT #
        self.assertEqual(main_program.EXIT_INVALID_USAGE,
                         exit_status,
                         'Exit Status')
        self.assertEqual('',
                         stdout_contents,
                         'Output on stdout')
        self.assertTrue(len(stderr_contents) > 0,
                        'An error message should be printed on stderr')

    def test_empty_file(self):
        # ARRANGE #
        test_case_source = ''
        with tmp_file_containing(test_case_source) as file_path:
            argv = [str(file_path)]
            # ACT #
            exit_status, stdout_contents, stderr_contents = execute_main_program(argv)
        # ASSERT #
        self.assertEqual(0,
                         exit_status,
                         'Exit Status')
        self.assertEqual(FullResultStatus.PASS.name + os.linesep,
                         stdout_contents,
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
            argv = [str(file_path)]
            # ACT #
            exit_status, stdout_contents, stderr_contents = execute_main_program(argv)
        # ASSERT #
        self.assertEqual(0,
                         exit_status,
                         'Exit Status')
        self.assertEqual(FullResultStatus.PASS.name + os.linesep,
                         stdout_contents,
                         'Output on stdout')


class TestHelp(unittest.TestCase):
    def test_invalid_usage(self):
        # ARRANGE #
        command_line_arguments = ['help', 'arg', 'arg', 'arg', 'arg']
        exit_status, stdout_contents, stderr_contents = execute_main_program(command_line_arguments)
        # ASSERT #
        self.assertEqual(main_program.EXIT_INVALID_USAGE,
                         exit_status,
                         'Exit Status')
        self.assertEqual('',
                         stdout_contents,
                         'Output on stdout')
        self.assertTrue(len(stderr_contents) > 0)

    def test_instructions(self):
        # ARRANGE #
        command_line_arguments = ['help', 'instructions']
        exit_status, stdout_contents, stderr_contents = execute_main_program(command_line_arguments)
        # ASSERT #
        self.assertEqual(0,
                         exit_status,
                         'Exit Status')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestTestCaseWithoutInstructions))
    ret_val.addTest(unittest.makeSuite(TestHelp))
    return ret_val


if __name__ == '__main__':
    unittest.main()
