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


class EmptySuite(main_program_check_for_test_suite.SetupWithoutPreprocessor):
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


class SuiteWithSingleEmptyTestCase(main_program_check_for_test_suite.SetupWithoutPreprocessor):
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

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'the.case', FullResultStatus.PASS.name),
            self.suite_end(root_path / 'main.suite'),
        ]

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

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return []

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

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return []

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

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'invalid-syntax.case', AccessErrorType.PARSE_ERROR.name),
            self.suite_end(root_path / 'main.suite'),
        ]

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

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        return [
            self.suite_begin(root_path / 'sub-sub.suite'),
            self.suite_end(root_path / 'sub-sub.suite'),

            self.suite_begin(root_path / 'sub.suite'),
            self.case(root_path / 'sub.case', FullResultStatus.PASS.name),
            self.suite_end(root_path / 'sub.suite'),

            self.suite_begin(root_path / 'main.suite'),
            self.case(root_path / 'main.case', FullResultStatus.PASS.name),
            self.suite_end(root_path / 'main.suite'),
        ]

    def expected_exit_code(self) -> int:
        return 0


class TestTestSuite(main_program_check_for_test_suite.TestsForSetupWithoutPreprocessorInternally):
    def test_invalid_usage(self):
        # ARRANGE #
        test_case_source = ''
        with tmp_file_containing(test_case_source) as file_path:
            argv = ['suite', '--invalid-option-that-should-cause-failure', str(file_path)]
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
        self._check(EmptySuite())

    def test_suite_with_single_empty_case(self):
        self._check(SuiteWithSingleEmptyTestCase())

    def test_suite_with_single_test_case_with_only_section_headers(self):
        self._check(SuiteWithSingleTestCaseWithOnlySectionHeaders())

    def test_suite_reference_to_non_existing_case_file(self):
        self._check(SuiteReferenceToNonExistingCaseFile())

    def test_suite_reference_to_non_existing_suite_file(self):
        self._check(SuiteReferenceToNonExistingSuiteFile())

    def test_suite_with_single_case_with_invalid_syntax(self):
        self._check(SuiteWithSingleCaseWithInvalidSyntax())

    def test_complex_successful_suite(self):
        self._check(ComplexSuccessfulSuite())


class TestTestSuiteWithWildcardFileReferencesToCaseFiles(
    main_program_check_for_test_suite.TestsForSetupWithoutPreprocessorInternally):
    def test_references_to_case_files_that_matches_no_files(self):
        self._check(wildcard.ReferencesToCaseFilesThatMatchesNoFiles())

    def test_references_to_case_files_that_are_directories(self):
        self._check(wildcard.ReferencesToCaseFilesThatAreDirectories())

    def test_references_to_case_files_that_matches_files__type_question_mark(self):
        self._check(wildcard.ReferencesToCaseFilesThatMatchesFilesTypeQuestionMark())

    def test_references_to_case_files_that_matches_files__type_character_range(self):
        self._check(wildcard.ReferencesToCaseFilesThatMatchesFilesTypeCharacterRange())

    def test_references_to_case_files_that_matches_files__type_negated_character_range(self):
        self._check(wildcard.ReferencesToCaseFilesThatMatchesFilesTypeNegatedCharacterRange())

    def test_references_to_case_files_in_subdir_that_matches(self):
        self._check(wildcard.ReferencesToCaseFilesInSubDirThatMatchesFiles())

    def test_references_to_case_files_in_any_direct_sub_dir(self):
        self._check(wildcard.ReferencesToCaseFilesInAnyDirectSubDir())

    def test_references_to_case_files_in_any_sub_dir(self):
        self._check(wildcard.ReferencesToCaseFilesInAnySubDir())


class TestTestSuiteWithWildcardFileReferencesToSuiteFiles(
    main_program_check_for_test_suite.TestsForSetupWithoutPreprocessorInternally):
    def test_references_to_suite_files_that_matches_no_files(self):
        self._check(wildcard.ReferencesToCaseFilesThatMatchesNoFiles())

    def test_references_to_suite_files_that_are_directories(self):
        self._check(wildcard.ReferencesToSuiteFilesThatAreDirectories())

    def test_references_to_suite_files_that_matches_files__type_question_mark(self):
        self._check(wildcard.ReferencesToSuiteFilesThatMatchesFilesTypeQuestionMark())

    def test_references_to_suite_files_that_matches_files__type_character_range(self):
        self._check(wildcard.ReferencesToSuiteFilesThatMatchesFilesTypeCharacterRange())

    def test_references_to_suite_files_that_matches_files__type_negated_character_range(self):
        self._check(wildcard.ReferencesToSuiteFilesThatMatchesFilesTypeNegatedCharacterRange())

    def test_references_to_suite_files_in_any_direct_subdir(self):
        self._check(wildcard.ReferencesToSuiteFilesInAnyDirectSubDir())

    def test_references_to_suite_files_in_any_sub_dir(self):
        self._check(wildcard.ReferencesToSuiteFilesInAnySubDir())


class TestTestSuitePreprocessing(main_program_check_for_test_suite.TestsForSetupWithPreprocessorInternally):
    def test_that_preprocessor_is_applied_with_test_case_file_as_argument(self):
        self._check(pre_proc_tests.PreprocessorIsAppliedWithTestCaseFileAsArgument())


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestTestSuite))
    ret_val.addTest(unittest.makeSuite(TestTestSuiteWithWildcardFileReferencesToCaseFiles))
    ret_val.addTest(unittest.makeSuite(TestTestSuiteWithWildcardFileReferencesToSuiteFiles))
    ret_val.addTest(unittest.makeSuite(TestTestSuitePreprocessing))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
