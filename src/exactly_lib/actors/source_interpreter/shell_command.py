import shlex

from exactly_lib.actors.source_interpreter import parser_and_executor as pa
from exactly_lib.actors.util.executor_made_of_parts import parts
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case.actor import AtcOsProcessExecutor, Actor
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.program.command import command_sdvs

ACT_PHASE_SOURCE_FILE_BASE_NAME = 'act-phase.src'


def actor(interpreter_shell_command: str) -> Actor:
    return parts.ActorFromParts(
        pa.Parser(),
        parts.UnconditionallySuccessfulValidatorConstructor(),
        _ExecutorConstructor(interpreter_shell_command)
    )


class _ExecutorConstructor(parts.ExecutorConstructor[pa.SourceInfo]):
    def __init__(self, interpreter_shell_command: str):
        self._interpreter_shell_command = interpreter_shell_command

    def construct(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_process_executor: AtcOsProcessExecutor,
                  object_to_execute: pa.SourceInfo) -> parts.Executor:
        return _Executor(os_process_executor,
                         self._interpreter_shell_command,
                         object_to_execute)


class _Executor(pa.ExecutorBase):
    def __init__(self,
                 os_process_executor: AtcOsProcessExecutor,
                 interpreter_shell_command: str,
                 source_info: pa.SourceInfo,
                 ):
        super().__init__(os_process_executor,
                         pa.ActSourceFileNameGeneratorForConstantFileName(ACT_PHASE_SOURCE_FILE_BASE_NAME),
                         source_info)
        self.interpreter_shell_command = interpreter_shell_command

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> CommandSdv:
        script_file_argument = shlex.quote(str(self.source_file_path))

        command_line_elements = string_sdvs.from_fragments([
            string_sdvs.str_fragment(self.interpreter_shell_command),
            string_sdvs.str_fragment(' '),
            string_sdvs.str_fragment(script_file_argument),
        ])

        return command_sdvs.for_shell(command_line_elements)
