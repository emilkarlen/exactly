import os
import pathlib
import unittest

from shellcheck_lib.default.execution_mode.test_suite.reporting import INVALID_SUITE_EXIT_CODE, FAILED_TESTS_EXIT_CODE
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.test_case_processing import AccessErrorType
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


class EmptySuite(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'empty.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('empty.suite', ''),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'empty.suite'),
            self.suite_end(root_path / 'empty.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


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


class SuiteWithSingleTestCaseWithOnlySectionHeaders(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              'the.case'])),
            File('the.case',
                 lines_content([
                     '[setup]',
                     '[act]',
                     '[assert]',
                     '[cleanup]',
                 ])),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'the.case', FullResultStatus.PASS.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class SuiteReferenceToNonExistingCaseFile(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              'non-existing.case'])),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_exit_code(self) -> int:
        return INVALID_SUITE_EXIT_CODE


class SuiteWithSingleCaseWithInvalidSyntax(check_suite.Setup):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              'invalid-syntax.case'])),
            File('invalid-syntax.case',
                 lines_content(['[invalid section]'])),
        ])

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'invalid-syntax.case', AccessErrorType.PARSE_ERROR.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return FAILED_TESTS_EXIT_CODE


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
        self._check([], EmptySuite())

    def test_suite_with_single_empty_case(self):
        self._check([], SuiteWithSingleEmptyTestCase())

    def test_suite_with_single_test_case_with_only_section_headers(self):
        self._check([], SuiteWithSingleTestCaseWithOnlySectionHeaders())

    def test_suite_reference_to_non_existing_case_file(self):
        self._check([], SuiteReferenceToNonExistingCaseFile())

    def test_suite_with_single_case_with_invalid_syntax(self):
        self._check([], SuiteWithSingleCaseWithInvalidSyntax())

    def _check(self,
               additional_arguments: list,
               setup: check_suite.Setup):
        check_suite.check(additional_arguments, setup, self)


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
