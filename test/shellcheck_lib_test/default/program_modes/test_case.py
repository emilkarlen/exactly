import unittest

from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.cli_environment import exit_values
from shellcheck_lib.document.syntax import section_header
from shellcheck_lib.execution import phases
from shellcheck_lib.util.string import lines_content
from shellcheck_lib_test.default.test_resources import default_main_program_case_preprocessing
from shellcheck_lib_test.default.test_resources.test_case_file_elements import phase_header_line
from shellcheck_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_with_preprocessor, \
    tests_for_setup_without_preprocessor
from shellcheck_lib_test.test_resources.main_program.main_program_check_for_test_case import SetupWithoutPreprocessor
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.main_program.main_program_runners import RunViaMainProgramInternally
from shellcheck_lib_test.test_resources.main_program.main_program_test_utils import process_result_for
from shellcheck_lib_test.test_resources.process import ExpectedSubProcessResult


class InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(SetupWithoutPreprocessor):
    def additional_arguments(self) -> list:
        return ['--invalid-option-that-should-cause-failure']

    def expected_result(self) -> ExpectedSubProcessResult:
        return ExpectedSubProcessResult(exitcode=main_program.EXIT_INVALID_USAGE,
                                        stdout='')

    def test_case(self) -> str:
        return ''


class EmptyTestCaseShouldPass(SetupWithoutPreprocessor):
    def expected_result(self) -> ExpectedSubProcessResult:
        return process_result_for(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        return ''


class AllPhasesEmptyShouldPass(SetupWithoutPreprocessor):
    def expected_result(self) -> ExpectedSubProcessResult:
        return process_result_for(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        test_case_lines = [phase_header_line(phase)
                           for phase in phases.ALL]
        return lines_content(test_case_lines)


class WhenAPhaseHasInvalidPhaseNameThenExitStatusShouldIndicateThis(SetupWithoutPreprocessor):
    def expected_result(self) -> ExpectedSubProcessResult:
        return process_result_for(exit_values.NO_EXECUTION__PARSE_ERROR)

    def test_case(self) -> str:
        test_case_lines = [
            section_header('invalid phase name'),
        ]
        return lines_content(test_case_lines)


MISC = [
    InvalidCommandLineOptionShouldExitWithInvalidUsageStatus(),
    EmptyTestCaseShouldPass(),
    AllPhasesEmptyShouldPass(),
    WhenAPhaseHasInvalidPhaseNameThenExitStatusShouldIndicateThis(),
]

PREPROCESSING_TESTS = [
    default_main_program_case_preprocessing.TransformationIntoTestCaseThatPass(),
    default_main_program_case_preprocessing.TransformationIntoTestCaseThatParserError(),
]


def suite_for_test_case_preprocessing(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return tests_for_setup_with_preprocessor(PREPROCESSING_TESTS,
                                             main_program_runner)


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(MISC, main_program_runner))
    ret_val.addTest(suite_for_test_case_preprocessing(main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(RunViaMainProgramInternally())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
