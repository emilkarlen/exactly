import pathlib
import shutil
import unittest

from shellcheck_lib.cli.main_program import EXIT_INVALID_USAGE
import shellcheck_lib.cli.utils
from shellcheck_lib.execution import execution_directory_structure
from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib_test.cli import default_main_program
from shellcheck_lib_test.execution.test_execution_directory_structure import \
    is_execution_directory_structure_after_execution
from shellcheck_lib_test.util.file_checks import FileChecker
from shellcheck_lib_test.util.cli_main_program_via_shell_utils.run import SUCCESSFUL_RESULT, \
    run_shellcheck_in_sub_process_with_file_argument, \
    contents_of_file
from shellcheck_lib_test.util.with_tmp_file import lines_content, SubProcessResult, \
    ExpectedSubProcessResult, SubProcessResultInfo
from shellcheck_lib_test.cli.cases import default_main_program_wildcard as wildcard
from shellcheck_lib_test.cli import default_main_program_suite_preprocessing as pre_proc_tests
from shellcheck_lib_test.util.main_program import main_program_check_for_test_case
from shellcheck_lib_test.cli import default_main_program_case_preprocessing
from shellcheck_lib_test.util.main_program import main_program_check_for_test_suite


class UnitTestCaseWithUtils(unittest.TestCase):
    def _run_shellcheck_in_sub_process(self,
                                       test_case_source: str,
                                       flags: list=()) -> SubProcessResultInfo:
        return run_shellcheck_in_sub_process_with_file_argument(self,
                                                                file_contents=test_case_source,
                                                                flags=flags)


class TestsInvokation(UnitTestCaseWithUtils):
    def test_exit_status_with_invalid_invokation_for_test_case(self):
        # ARRANGE #
        test_case_source = ''
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source,
                                                     flags=['--illegal-flag-42847920189']).sub_process_result
        # ASSERT #
        self.assertEqual(EXIT_INVALID_USAGE,
                         actual.exitcode,
                         'Expected exit code for invalid invokation')
        self.assertEqual('',
                         actual.stdout,
                         'Expects no output on stdout for invalid invokation')

    def test_exit_status_with_invalid_invokation_for_test_suite(self):
        # ARRANGE #
        test_suite_source = ''
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_suite_source,
                                                     flags=['suite', '--illegal-flag-42847920189']).sub_process_result
        # ASSERT #
        self.assertEqual(EXIT_INVALID_USAGE,
                         actual.exitcode,
                         'Expected exit code for invalid invokation')
        self.assertEqual('',
                         actual.stdout,
                         'Expects no output on stdout for invalid invokation')

    def test_exit_status_with_invalid_invokation_for_help(self):
        # ARRANGE #
        test_suite_source = ''
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_suite_source,
                                                     flags=['help', '--illegal-flag-42847920189']).sub_process_result
        # ASSERT #
        self.assertEqual(EXIT_INVALID_USAGE,
                         actual.exitcode,
                         'Expected exit code for invalid invokation')
        self.assertEqual('',
                         actual.stdout,
                         'Expects no output on stdout for invalid invokation')


class BasicTestsWithNoCliFlags(UnitTestCaseWithUtils):
    def test_empty_test_case(self):
        # ARRANGE #
        test_case_source = ''
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source).sub_process_result
        # ASSERT #
        SUCCESSFUL_RESULT.assert_matches(self,
                                         actual)

    def test_test_case_with_only_phase_headers(self):
        # ARRANGE #
        test_case_source_lines = [
            '[setup]',
            '[act]',
            '[assert]',
            '[cleanup]',
        ]
        test_case_source = lines_content(test_case_source_lines)
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source).sub_process_result
        # ASSERT #
        SUCCESSFUL_RESULT.assert_matches(self,
                                         actual)


class TestsWithPreservedExecutionDirectoryStructure(UnitTestCaseWithUtils):
    def test_flag_for_printing_and_preserving_eds(self):
        # ARRANGE #
        test_case_source = ''
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source,
                                                     flags=['--keep']).sub_process_result
        # ASSERT #
        actual_eds_directory = self._get_printed_eds_or_fail(actual)
        actual_eds_path = pathlib.Path(actual_eds_directory)
        if actual_eds_path.exists():
            if actual_eds_path.is_dir():
                is_execution_directory_structure_after_execution(
                    FileChecker(self, 'Not an Execution Directory Structure'),
                    actual_eds_directory)
                self._remove_if_is_directory(actual_eds_directory)
            else:
                self.fail('Output from program is not the EDS (not a directory): "%s"' % actual_eds_directory)
        else:
            self.fail('The output from the program is not the EDS: "%s"' % actual_eds_directory)
        expected = ExpectedSubProcessResult(exitcode=FullResultStatus.PASS.value,
                                            stderr='')
        expected.assert_matches(self,
                                actual)

    def test_environment_variables(self):
        # ARRANGE #
        test_case_source_lines = [
            '[act]',
            'import os',
            self._print_variable_name__equals__variable_value(
                environment_variables.ENV_VAR_HOME),
            self._print_variable_name__equals__variable_value(
                environment_variables.ENV_VAR_TEST),
            self._print_variable_name__equals__variable_value(
                environment_variables.ENV_VAR_TMP),
        ]
        test_case_source = lines_content(test_case_source_lines)
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source,
                                                     flags=['--interpreter',
                                                            shellcheck_lib.cli.utils.INTERPRETER_FOR_TEST,
                                                            '--keep'])
        # ASSERT #
        self.assertEqual(FullResultStatus.PASS.value,
                         actual.sub_process_result.exitcode,
                         'Program is expected to have executed successfully')
        actual_eds_directory = self._get_printed_eds_or_fail(actual.sub_process_result)
        eds = execution_directory_structure.ExecutionDirectoryStructure(actual_eds_directory)
        actually_printed_variables = self._get_act_output_to_stdout(eds).splitlines()
        expected_printed_variables = [
            '%s=%s' % (environment_variables.ENV_VAR_HOME, str(actual.file_argument.parent)),
            '%s=%s' % (environment_variables.ENV_VAR_TEST, str(eds.test_root_dir)),
            '%s=%s' % (environment_variables.ENV_VAR_TMP, str(eds.tmp_dir)),
        ]
        self.assertEqual(expected_printed_variables,
                         actually_printed_variables,
                         'Environment variables printed by the act script')
        self._remove_if_is_directory(actual_eds_directory)

    def _remove_if_is_directory(self, actual_eds_directory: str):
        actual_eds_path = pathlib.Path(actual_eds_directory)
        if actual_eds_path.is_dir():
            shutil.rmtree(actual_eds_directory)

    def _get_printed_eds_or_fail(self, actual: SubProcessResult) -> str:
        printed_lines = actual.stdout.splitlines()
        self.assertEqual(1,
                         len(printed_lines),
                         'Number of printed printed lines should be exactly 1')
        actual_eds_directory = printed_lines[0]
        return actual_eds_directory

    @staticmethod
    def _print_variable_name__equals__variable_value(variable_name: str) -> str:
        return 'print("%s=" + os.environ["%s"])' % (variable_name, variable_name)

    def _get_act_output_to_stdout(self,
                                  eds: execution_directory_structure.ExecutionDirectoryStructure) -> str:
        return contents_of_file(eds.result.std.stdout_file)


class TestsExecuteActPhase(UnitTestCaseWithUtils):
    def test_that_output_and_exit_code_from_act_phase_is_emitted_as_result_of_shellcheck(self):
        # ARRANGE #
        test_case_source = """
[act]
import os
import sys
sys.stdout.write("output to stdout")
sys.stderr.write("output to stderr\\n")
sys.exit(72)
"""
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source,
                                                     flags=['--interpreter',
                                                            shellcheck_lib.cli.utils.INTERPRETER_FOR_TEST,
                                                            '--act']).sub_process_result
        # ASSERT #
        self.assertEqual(72,
                         actual.exitcode,
                         'Program is expected to exit with same exit code as act script')
        self.assertEqual('output to stdout',
                         actual.stdout,
                         'Output on stdout is expected to be same as that of act script')
        self.assertEqual('output to stderr\n',
                         actual.stderr,
                         'Output on stderr is expected to be same as that of act script')


class TestTestCasePreprocessing(
    main_program_check_for_test_case.TestsForSetupWithPreprocessorExternally):
    def test_transformation_into_test_case_that_pass(self):
        self._check([],
                    default_main_program_case_preprocessing.TransformationIntoTestCaseThatPass())

    def test_transformation_into_test_case_that_parser_error(self):
        self._check([],
                    default_main_program_case_preprocessing.TransformationIntoTestCaseThatParserError())


class TestTestSuite(main_program_check_for_test_suite.TestsForSetupWithoutPreprocessorExternally):
    def test_empty_file(self):
        self._check([], default_main_program.EmptySuite())

    def test_suite_with_single_empty_case(self):
        self._check([], default_main_program.SuiteWithSingleEmptyTestCase())

    def test_suite_with_single_test_case_with_only_section_headers(self):
        self._check([], default_main_program.SuiteWithSingleTestCaseWithOnlySectionHeaders())

    def test_suite_reference_to_non_existing_case_file(self):
        self._check([], default_main_program.SuiteReferenceToNonExistingCaseFile())

    def test_suite_reference_to_non_existing_suite_file(self):
        self._check([], default_main_program.SuiteReferenceToNonExistingSuiteFile())

    def test_suite_with_single_case_with_invalid_syntax(self):
        self._check([], default_main_program.SuiteWithSingleCaseWithInvalidSyntax())

    def test_complex_successful_suite(self):
        self._check([], default_main_program.ComplexSuccessfulSuite())


class TestTestSuitesWithWildcardFileReferences(
    main_program_check_for_test_suite.TestsForSetupWithoutPreprocessorExternally):
    def test_references_to_case_files_that_matches_no_files(self):
        self._check([], wildcard.ReferencesToCaseFilesThatMatchesNoFiles())

    def test_references_to_case_files_that_are_directories(self):
        self._check([], wildcard.ReferencesToCaseFilesThatAreDirectories())

    def test_references_to_suite_files_that_matches_no_files(self):
        self._check([], wildcard.ReferencesToSuiteFilesThatMatchesNoFiles())

    def test_references_to_case_files_that_matches_files__type_question_mark(self):
        self._check([], wildcard.ReferencesToCaseFilesThatMatchesFilesTypeQuestionMark())

    def test_references_to_case_files_in_any_direct_sub_dir(self):
        self._check([], wildcard.ReferencesToCaseFilesInAnyDirectSubDir())

    def test_references_to_suite_files_that_are_directories(self):
        self._check([], wildcard.ReferencesToSuiteFilesThatAreDirectories())

    def test_references_to_suite_files_that_matches_files__type_character_range(self):
        self._check([], wildcard.ReferencesToSuiteFilesThatMatchesFilesTypeCharacterRange())

    def test_references_to_suite_files_that_matches_files__type_negated_character_range(self):
        self._check([], wildcard.ReferencesToSuiteFilesThatMatchesFilesTypeNegatedCharacterRange())

    def test_references_to_suite_files_in_any_sub_dir(self):
        self._check([], wildcard.ReferencesToSuiteFilesInAnySubDir())


class TestTestSuitePreprocessing(main_program_check_for_test_suite.TestsForSetupWithPreprocessorExternally):
    def test_empty_file(self):
        self._check([], pre_proc_tests.PreprocessorIsAppliedWithTestCaseFileAsArgument())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestsInvokation))
    ret_val.addTest(unittest.makeSuite(BasicTestsWithNoCliFlags))
    ret_val.addTest(unittest.makeSuite(TestsWithPreservedExecutionDirectoryStructure))
    ret_val.addTest(unittest.makeSuite(TestsExecuteActPhase))
    ret_val.addTest(unittest.makeSuite(TestTestCasePreprocessing))
    ret_val.addTest(unittest.makeSuite(TestTestSuite))
    ret_val.addTest(unittest.makeSuite(TestTestSuitesWithWildcardFileReferences))
    ret_val.addTest(unittest.makeSuite(TestTestSuitePreprocessing))
    return ret_val


if __name__ == '__main__':
    unittest.main()
