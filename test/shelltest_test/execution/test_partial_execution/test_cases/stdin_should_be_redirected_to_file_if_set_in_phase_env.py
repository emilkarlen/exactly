"""
Checks that output to stdout, stderr and the exit code are saved in the correct locations.
"""
import unittest

from shelltest.test_case.success_or_hard_error_construction import new_success
from shelltest.test_case import success_or_validation_hard_or_error_construction
from shelltest_test.execution.util import utils
from shelltest_test.execution.util import py_unit_test_case
from shelltest_test.execution.util.py_unit_test_case import TestCaseWithCommonDefaultForSetupAssertCleanup
from shelltest.test_case import instructions


INPUT_TMP_FILE = 'input.txt'

EXPECTED_EXIT_CODE = 0
TEXT_ON_STDIN = 'on stdin'
EXPECTED_CONTENTS_OF_STDERR = ''


class TestCaseDocument(TestCaseWithCommonDefaultForSetupAssertCleanup):
    def _setup_phase(self) -> list:
        return [
            self._next_instruction_line(
                PyCommandThatStoresStringInFileInCurrentDirectory(INPUT_TMP_FILE,
                                                                  TEXT_ON_STDIN))
        ]

    def _act_phase(self) -> list:
        return [
            self._next_instruction_line(InstructionThatSetsStdinFileName(INPUT_TMP_FILE)),
            self._next_instruction_line(StatementsThatCopiesStdinToStdout())
        ]


def assertions(utc: unittest.TestCase,
               actual: py_unit_test_case.Result):
    utils.assert_is_file_with_contents(
        utc,
        actual.execution_directory_structure.result.exitcode_file,
        str(EXPECTED_EXIT_CODE))
    utils.assert_is_file_with_contents(
        utc,
        actual.execution_directory_structure.result.std.stdout_file,
        TEXT_ON_STDIN)
    utils.assert_is_file_with_contents(
        utc,
        actual.execution_directory_structure.result.std.stderr_file,
        EXPECTED_CONTENTS_OF_STDERR)


class PyCommandThatStoresStringInFileInCurrentDirectory(instructions.SetupPhaseInstruction):
    def __init__(self,
                 file_base_name: str,
                 text_to_store: str):
        super().__init__()
        self.__file_base_name = file_base_name
        self.__text_to_store = text_to_store

    def validate(self,
                 global_environment: instructions.GlobalEnvironmentForPreEdsStep) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def main(self,
             global_environment: instructions.GlobalEnvironmentForNamedPhase,
             phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        with open(self.__file_base_name, 'w') as f:
            f.write(self.__text_to_store)
        return new_success()


class StatementsThatCopiesStdinToStdout(instructions.ActPhaseInstruction):
    def __init__(self):
        super().__init__()

    def validate(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def main(self,
             global_environment: instructions.GlobalEnvironmentForNamedPhase,
             phase_environment: instructions.PhaseEnvironmentForScriptGeneration) \
            -> instructions.SuccessOrHardError:
        statements = [
            'import sys',
            'sys.stdout.write(sys.stdin.read())',
        ]
        phase_environment.append.raw_script_statements(statements)
        return new_success()


class InstructionThatSetsStdinFileName(instructions.ActPhaseInstruction):
    def __init__(self,
                 file_name: str):
        super().__init__()
        self.__file_name = file_name

    def validate(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def main(self,
             global_environment: instructions.GlobalEnvironmentForNamedPhase,
             phase_environment: instructions.PhaseEnvironmentForScriptGeneration) -> instructions.SuccessOrHardError:
        phase_environment.set_stdin_file(self.__file_name)
        return new_success()
