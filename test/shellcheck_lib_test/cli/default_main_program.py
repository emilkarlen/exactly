import os
import pathlib
import unittest

from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib_test.cli.utils import check_suite
from shellcheck_lib_test.cli.utils.execute_main_program import execute_main_program
from shellcheck_lib_test.util.file_structure import DirContents, File
from shellcheck_lib_test.util.with_tmp_file import tmp_file_containing, tmp_file_containing_lines, lines_content
from shellcheck_lib.cli import main_program


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


class SuiteWithSingleEmptyTestCase(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]', 'the.case'])),
            File('the.case', ''),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'the.case', FullResultStatus.PASS.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class TestTestSuite(unittest.TestCase):
    def test_invalid_usage(self):
        # ARRANGE #
        test_case_source = ''
        with tmp_file_containing(test_case_source) as file_path:
            argv = ['suite', '--invalid-option-that-should-cause-failure', str(file_path)]
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
            argv = ['suite', str(file_path)]
            # ACT #
            exit_status, stdout_contents, stderr_contents = execute_main_program(argv)
        # ASSERT #
        self.assertEqual(0,
                         exit_status,
                         'Exit Status')
        output = lines_content(['SUITE ' + str(file_path) + ': BEGIN',
                                'SUITE ' + str(file_path) + ': END'])
        self.assertEqual(output,
                         stdout_contents,
                         'Output on stdout')

    def test_suite_with_single_empty_case(self):
        check_suite.check([], SuiteWithSingleEmptyTestCase(), self)


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
    ret_val.addTest(unittest.makeSuite(TestTestSuite))
    ret_val.addTest(unittest.makeSuite(TestHelp))
    return ret_val


if __name__ == '__main__':
    unittest.main()
