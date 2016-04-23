import pathlib
import unittest

from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.cli_environment.exit_values import NO_EXECUTION__PARSE_ERROR, EXECUTION__PASS
from shellcheck_lib.default.program_modes.test_suite.reporting import INVALID_SUITE_EXIT_CODE, FAILED_TESTS_EXIT_CODE
from shellcheck_lib.util.string import lines_content
from shellcheck_lib_test.default.test_resources import default_main_program_suite_preprocessing as pre_proc_tests
from shellcheck_lib_test.default.test_resources import default_main_program_wildcard as wildcard
from shellcheck_lib_test.default.test_resources.internal_main_program_runner import RunViaMainProgramInternally
from shellcheck_lib_test.test_resources.file_structure import DirContents, File
from shellcheck_lib_test.test_resources.main_program import main_program_check_for_test_suite
from shellcheck_lib_test.test_resources.main_program.main_program_check_base import \
    tests_for_setup_without_preprocessor, tests_for_setup_with_preprocessor
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.program_modes.suite import reporting_output


class InvalidOptions(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite', ''), ])

    def additional_arguments(self) -> list:
        return ['--invalid-option-that-should-cause-failure']

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return main_program.EXIT_INVALID_USAGE


class EmptySuite(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'empty.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('empty.suite', ''),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'empty.suite'),
            reporting_output.suite_end(root_path / 'empty.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class SuiteWithSingleEmptyTestCase(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]', 'the.case'])),
            File('the.case', ''),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / 'the.case', EXECUTION__PASS.exit_identifier),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class SuiteWithSingleTestCaseWithOnlySectionHeaders(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              'the.case'])),
            File('the.case',
                 lines_content([
                     '[conf]',
                     '[setup]',
                     '[act]',
                     '[assert]',
                     '[before-assert]',
                     '[cleanup]',
                 ])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / 'the.case', EXECUTION__PASS.exit_identifier),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


class SuiteReferenceToNonExistingCaseFile(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              'non-existing.case'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return INVALID_SUITE_EXIT_CODE


class SuiteReferenceToNonExistingSuiteFile(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              'non-existing.suite'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return []

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return INVALID_SUITE_EXIT_CODE


class SuiteWithSingleCaseWithInvalidSyntax(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]',
                                              'invalid-syntax.case'])),
            File('invalid-syntax.case',
                 lines_content(['[invalid section]'])),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / 'invalid-syntax.case', NO_EXECUTION__PARSE_ERROR.exit_identifier),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return FAILED_TESTS_EXIT_CODE


class ComplexSuccessfulSuite(main_program_check_for_test_suite.SetupWithoutPreprocessor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[suites]',
                                              'sub.suite',
                                              '[cases]',
                                              'main.case'])),
            File('main.case', ''),
            File('sub.suite', lines_content(['[suites]',
                                             'sub-sub.suite',
                                             '[cases]',
                                             'sub.case'])),
            File('sub.case', ''),
            File('sub-sub.suite', ''),
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        return [
            reporting_output.suite_begin(root_path / 'sub-sub.suite'),
            reporting_output.suite_end(root_path / 'sub-sub.suite'),

            reporting_output.suite_begin(root_path / 'sub.suite'),
            reporting_output.case(root_path / 'sub.case', EXECUTION__PASS.exit_identifier),
            reporting_output.suite_end(root_path / 'sub.suite'),

            reporting_output.suite_begin(root_path / 'main.suite'),
            reporting_output.case(root_path / 'main.case', EXECUTION__PASS.exit_identifier),
            reporting_output.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        return reporting_output.summary(root_path)

    def expected_exit_code(self) -> int:
        return 0


BASIC_TESTS = [
    InvalidOptions(),
    EmptySuite(),
    SuiteWithSingleEmptyTestCase(),
    SuiteWithSingleTestCaseWithOnlySectionHeaders(),
    SuiteReferenceToNonExistingCaseFile(),
    SuiteReferenceToNonExistingSuiteFile(),
    SuiteWithSingleCaseWithInvalidSyntax(),
    ComplexSuccessfulSuite(),
]

TESTS_WITH_WILDCARD_FILE_REFERENCES_TO_CASE_FILES = [
    wildcard.ReferencesToCaseFilesThatMatchesNoFiles(),
    wildcard.ReferencesToCaseFilesThatAreDirectories(),
    wildcard.ReferencesToCaseFilesThatMatchesFilesTypeQuestionMark(),
    wildcard.ReferencesToCaseFilesThatMatchesFilesTypeCharacterRange(),
    wildcard.ReferencesToCaseFilesThatMatchesFilesTypeNegatedCharacterRange(),
    wildcard.ReferencesToCaseFilesInSubDirThatMatchesFiles(),
    wildcard.ReferencesToCaseFilesInAnyDirectSubDir(),
    wildcard.ReferencesToCaseFilesInAnySubDir(),
]

TESTS_WITH_WILDCARD_FILE_REFERENCES_TO_SUITE_FILES = [
    wildcard.ReferencesToSuiteFilesThatAreDirectories(),
    wildcard.ReferencesToSuiteFilesThatMatchesFilesTypeQuestionMark(),
    wildcard.ReferencesToSuiteFilesThatMatchesFilesTypeCharacterRange(),
    wildcard.ReferencesToSuiteFilesThatMatchesFilesTypeNegatedCharacterRange(),
    wildcard.ReferencesToSuiteFilesInAnyDirectSubDir(),
    wildcard.ReferencesToSuiteFilesInAnySubDir(),
]

TEST_TEST_SUITE_PREPROCESSING = [
    pre_proc_tests.PreprocessorIsAppliedWithTestCaseFileAsArgument()
]


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(
        tests_for_setup_without_preprocessor(BASIC_TESTS,
                                             main_program_runner))
    ret_val.addTest(
        tests_for_setup_without_preprocessor(TESTS_WITH_WILDCARD_FILE_REFERENCES_TO_CASE_FILES,
                                             main_program_runner))
    ret_val.addTest(
        tests_for_setup_without_preprocessor(TESTS_WITH_WILDCARD_FILE_REFERENCES_TO_SUITE_FILES,
                                             main_program_runner))
    ret_val.addTest(
        tests_for_setup_with_preprocessor(TEST_TEST_SUITE_PREPROCESSING,
                                          main_program_runner))
    return ret_val


def suite_for_running_main_program_internally() -> unittest.TestSuite:
    return suite_for(RunViaMainProgramInternally())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite_for_running_main_program_internally())
