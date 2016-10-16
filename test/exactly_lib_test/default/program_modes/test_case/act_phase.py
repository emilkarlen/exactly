import pathlib
import unittest

from exactly_lib.cli.cli_environment.program_modes.test_case import exit_values
from exactly_lib.execution import phases
from exactly_lib.util.string import lines_content
from exactly_lib_test.default.test_resources.internal_main_program_runner import RunViaMainProgramInternally
from exactly_lib_test.default.test_resources.test_case_file_elements import phase_header_line
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor, \
    TestForSetupWithoutPreprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndTestActor, SetupWithoutPreprocessorAndDefaultActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process_result_info_assertions import process_result_for_exit_value
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_without_preprocessor(TESTS, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(RunViaMainProgramInternally())


class EmptyTestCaseShouldFailDueToMissingActPhase(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> va.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__VALIDATE)

    def test_case(self) -> str:
        return ''


class TCForDebugging(unittest.TestCase):
    def runTest(self):
        tc = TestForSetupWithoutPreprocessor(
            ActPhaseShouldBeDefaultPhaseAndDefaultActorShouldBeActorForSingleExecutableProgramRelHome(),
            RunViaMainProgramInternally())
        tc.runTest()


class ActPhaseShouldBeDefaultPhaseAndDefaultActorShouldBeActorForSingleExecutableProgramRelHome(
    SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> va.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def _additional_files_in_file_structure(self, root_path: pathlib.Path) -> list:
        return [
            fs.python_executable_file('system-under-test',
                                      _PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0)
        ]

    def test_case(self) -> str:
        return lines_content(['system-under-test'])


class AllPhasesEmptyShouldPass(SetupWithoutPreprocessorAndTestActor):
    def test_case(self) -> str:
        test_case_lines = [phase_header_line(phase)
                           for phase in phases.ALL]
        return lines_content(test_case_lines)

    def expected_result(self) -> va.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)


TESTS = [
    EmptyTestCaseShouldFailDueToMissingActPhase(),
    ActPhaseShouldBeDefaultPhaseAndDefaultActorShouldBeActorForSingleExecutableProgramRelHome(),
    AllPhasesEmptyShouldPass(),
]

_PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0 = lines_content(['import sys',
                                                           'sys.exit(0)'])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
