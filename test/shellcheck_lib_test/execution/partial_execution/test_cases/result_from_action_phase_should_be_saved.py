"""
Checks that output to stdout, stderr and the exit code are saved in the correct locations.
"""

import unittest

from shellcheck_lib.test_case.sections import common
from shellcheck_lib.test_case.sections.act.instruction import PhaseEnvironmentForScriptGeneration, ActPhaseInstruction
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib_test.execution.partial_execution.test_resources.basic import \
    TestCaseWithCommonDefaultInstructions, Result
from shellcheck_lib_test.test_resources.execution.eds_test import ResultFilesCheck

_TEXT_ON_STDOUT = 'on stdout'
_TEXT_ON_STDERR = 'on stderr'
_EXIT_CODE = 5


class TestCaseDocument(TestCaseWithCommonDefaultInstructions):
    def _act_phase(self) -> list:
        return self.instruction_line_constructor.apply_list([
            ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr(_EXIT_CODE,
                                                                _TEXT_ON_STDOUT,
                                                                _TEXT_ON_STDERR),
        ])


def assertions(utc: unittest.TestCase,
               actual: Result):
    result_check = ResultFilesCheck(_EXIT_CODE,
                                    _TEXT_ON_STDOUT,
                                    _TEXT_ON_STDERR)
    result_check.apply(utc, actual.execution_directory_structure)


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
