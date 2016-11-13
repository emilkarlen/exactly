import pathlib
import unittest

from exactly_lib.execution import exit_values
from exactly_lib.util.string import lines_content
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    run_via_main_program_internally_with_default_setup
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor, \
    TestForSetupWithoutPreprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndDefaultActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    process_result_for_exit_value


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(TESTS, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(run_via_main_program_internally_with_default_setup())


class EmptyTestCaseShouldFailDueToMissingActPhase(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> va.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__VALIDATE)

    def test_case(self) -> str:
        return ''


class TCForDebugging(unittest.TestCase):
    def runTest(self):
        tc = TestForSetupWithoutPreprocessor(
            DefaultActorShouldSucceedWhenActPhaseIsASingleCommandLineOfAnExecutableProgramRelHome(),
            run_via_main_program_internally_with_default_setup())
        tc.runTest()


class DefaultActorShouldSucceedWhenActPhaseIsASingleCommandLineOfAnExecutableProgramRelHome(
    SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> va.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def _additional_files_in_file_structure(self, root_path: pathlib.Path) -> list:
        return [
            fs.python_executable_file('system-under-test',
                                      PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0)
        ]

    def test_case(self) -> str:
        return lines_content(['system-under-test'])


class DefaultActorShouldFailWhenActPhaseIsMultipleCommandLines(
    SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> va.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__VALIDATE)

    def _additional_files_in_file_structure(self, root_path: pathlib.Path) -> list:
        return [
            fs.python_executable_file('system-under-test',
                                      PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0)
        ]

    def test_case(self) -> str:
        return lines_content(['system-under-test',
                              'system-under-test'])


TESTS = [
    EmptyTestCaseShouldFailDueToMissingActPhase(),
    DefaultActorShouldSucceedWhenActPhaseIsASingleCommandLineOfAnExecutableProgramRelHome(),
    DefaultActorShouldFailWhenActPhaseIsMultipleCommandLines(),
]

PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0 = lines_content(['import sys',
                                                          'sys.exit(0)'])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
