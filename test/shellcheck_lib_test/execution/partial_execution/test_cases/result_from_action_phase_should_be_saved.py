"""
Checks that output to stdout, stderr and the exit code are saved in the correct locations.
"""

import unittest

from shellcheck_lib.test_case.sections import common
from shellcheck_lib.test_case.sections.act.instruction import PhaseEnvironmentForScriptGeneration, ActPhaseInstruction
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib_test.execution.test_resources import py_unit_test_case
from shellcheck_lib_test.execution.test_resources import utils
from shellcheck_lib_test.execution.test_resources.py_unit_test_case import \
    TestCaseWithCommonDefaultForSetupAssertCleanup

_TEXT_ON_STDOUT = 'on stdout'
_TEXT_ON_STDERR = 'on stderr'
_EXIT_CODE = 5


class TestCaseDocument(TestCaseWithCommonDefaultForSetupAssertCleanup):
    def _act_phase(self) -> list:
        return [
            self._next_instruction_line(
                ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr(_EXIT_CODE,
                                                                    _TEXT_ON_STDOUT,
                                                                    _TEXT_ON_STDERR))
        ]


def assertions(utc: unittest.TestCase,
               actual: py_unit_test_case.Result):
    utils.assert_is_file_with_contents(
        utc,
        actual.execution_directory_structure.result.exitcode_file,
        str(_EXIT_CODE))
    utils.assert_is_file_with_contents(
        utc,
        actual.execution_directory_structure.result.stdout_file,
        _TEXT_ON_STDOUT)
    utils.assert_is_file_with_contents(
        utc,
        actual.execution_directory_structure.result.stderr_file,
        _TEXT_ON_STDERR)


class ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr(ActPhaseInstruction):
    def __init__(self,
                 exit_code: int,
                 text_on_stdout: str,
                 text_on_stderr: str):
        super().__init__()
        self.__text_on_stdout = text_on_stdout
        self.__text_on_stderr = text_on_stderr
        self.__exit_code = exit_code

    def main(
            self,
            global_environment: common.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        statements = [
            'import sys',
            self.write_on('sys.stdout', self.__text_on_stdout),
            self.write_on('sys.stderr', self.__text_on_stderr),
            'sys.exit(%d)' % self.__exit_code
        ]
        phase_environment.append.raw_script_statements(statements)
        return sh.new_sh_success()

    @staticmethod
    def write_on(output_file: str,
                 text: str) -> str:
        return "%s.write('%s')" % (output_file, text)
