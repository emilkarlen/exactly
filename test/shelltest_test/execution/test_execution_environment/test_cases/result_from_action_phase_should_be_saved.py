from shelltest.exec_abs_syn.success_or_hard_error_construction import new_success
from shelltest.exec_abs_syn import success_or_validation_hard_or_error_construction
from shelltest.exec_abs_syn import instructions
from shelltest_test.execution.util.py_unit_test_case import UnitTestCaseForPy3Language


class TestCase(UnitTestCaseForPy3Language):
    """
    Checks that output to stdout, stderr and the exit code are saved in the correct locations.
    """

    TEXT_ON_STDOUT = 'on stdout'
    TEXT_ON_STDERR = 'on stderr'
    EXIT_CODE = 5

    def _act_phase(self) -> list:
        return [
            self._next_instruction_line(
                ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr(self.EXIT_CODE,
                                                                    self.TEXT_ON_STDOUT,
                                                                    self.TEXT_ON_STDERR))
        ]

    def _assertions(self):
        self.assert_is_regular_file_with_contents(self.eds.result.exitcode_file,
                                                  str(self.EXIT_CODE))
        self.assert_is_regular_file_with_contents(self.eds.result.std.stdout_file,
                                                  self.TEXT_ON_STDOUT)
        self.assert_is_regular_file_with_contents(self.eds.result.std.stderr_file,
                                                  self.TEXT_ON_STDERR)


class ActPhaseInstructionThatPrintsPathsOnStdoutAndStderr(instructions.ActPhaseInstruction):
    def __init__(self,
                 exit_code: int,
                 text_on_stdout: str,
                 text_on_stderr: str):
        super().__init__()
        self.__text_on_stdout = text_on_stdout
        self.__text_on_stderr = text_on_stderr
        self.__exit_code = exit_code

    def validate(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def update_phase_environment(
            self,
            phase_name: str,
            global_environment: instructions.GlobalEnvironmentForNamedPhase,
            phase_environment: instructions.PhaseEnvironmentForScriptGeneration) -> instructions.SuccessOrHardError:
        statements = [
            'import sys',
            self.write_on('sys.stdout', self.__text_on_stdout),
            self.write_on('sys.stderr', self.__text_on_stderr),
            'sys.exit(%d)' % self.__exit_code
        ]
        phase_environment.append.raw_script_statements(statements)
        return new_success()

    @staticmethod
    def write_on(output_file: str,
                 text: str) -> str:
        return "%s.write('%s')" % (output_file, text)
