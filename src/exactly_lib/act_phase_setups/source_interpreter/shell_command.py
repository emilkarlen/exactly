import pathlib
import shlex

from exactly_lib.act_phase_setups.source_interpreter import parser_and_executor as pa
from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling, ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.process_execution.os_process_execution import Command

ACT_PHASE_SOURCE_FILE_BASE_NAME = 'act-phase.src'


def handling_for_interpreter_command(interpreter_shell_command: str) -> ActPhaseHandling:
    return ActPhaseHandling(Constructor(interpreter_shell_command))


class Constructor(parts.Constructor):
    def __init__(self, interpreter_shell_command: str):
        super().__init__(pa.Parser(),
                         parts.UnconditionallySuccessfulValidator,
                         lambda ope, environment, source_code: Executor(ope, interpreter_shell_command, source_code))


class Executor(pa.ExecutorBase):
    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 interpreter_shell_command: str,
                 source_info: pa.SourceInfo):
        super().__init__(os_process_executor,
                         pa.ActSourceFileNameGeneratorForConstantFileName(ACT_PHASE_SOURCE_FILE_BASE_NAME),
                         source_info)
        self.interpreter_shell_command = interpreter_shell_command

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        script_file_path = self._source_file_path(script_output_dir_path)
        script_file_argument = shlex.quote(str(script_file_path))
        cmd = self.interpreter_shell_command + ' ' + script_file_argument
        return Command(cmd, shell=True)
