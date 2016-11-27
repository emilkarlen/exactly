import pathlib
import unittest

from exactly_lib.execution.exit_values import EXECUTION__PASS
from exactly_lib.test_suite import exit_values
from exactly_lib.util.string import lines_content
from exactly_lib_test.default.program_modes.test_case.act_phase import PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    run_via_main_program_internally_with_default_setup
from exactly_lib_test.test_resources.file_structure import DirContents, File, python_executable_file
from exactly_lib_test.test_resources.main_program import main_program_check_for_test_suite
from exactly_lib_test.test_resources.main_program.main_program_check_base import \
    tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_suite.reporters.test_resources import simple_progress_reporter_output


class SuiteWithSingleTestCaseThatInvokesSuccessfulCommandUsingDefaultActor(
    main_program_check_for_test_suite.SetupWithoutPreprocessorWithDefaultActor):
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            File('main.suite', lines_content(['[cases]', 'the.case'])),
            File('the.case', lines_content(['[act]',
                                            'system-under-test',
                                            '[assert]',
                                            'exitcode 0'])),
            python_executable_file('system-under-test',
                                   PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0)
        ])

    def expected_stdout_run_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return [
            expected_line.suite_begin(root_path / 'main.suite'),
            expected_line.case(root_path / 'the.case', EXECUTION__PASS.exit_identifier),
            expected_line.suite_end(root_path / 'main.suite'),
        ]

    def expected_stdout_reporting_lines(self, root_path: pathlib.Path) -> list:
        expected_line = simple_progress_reporter_output.ExpectedLine(root_path)
        return expected_line.summary_for_valid_suite(root_path, exit_values.ALL_PASS)

    def expected_exit_code(self) -> int:
        return exit_values.ALL_PASS.exit_code


_TESTS = [
    SuiteWithSingleTestCaseThatInvokesSuccessfulCommandUsingDefaultActor(),
]


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(
        tests_for_setup_without_preprocessor(_TESTS,
                                             main_program_runner))
    return ret_val


def suite_for_running_main_program_internally() -> unittest.TestSuite:
    return suite_for(run_via_main_program_internally_with_default_setup())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite_for_running_main_program_internally())
