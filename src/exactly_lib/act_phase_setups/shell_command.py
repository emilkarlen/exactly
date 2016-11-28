import pathlib

from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import CommandExecutor
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.util.process_execution.os_process_execution import Command


def act_phase_setup() -> ActPhaseSetup:
    return ActPhaseSetup(Constructor())


class Constructor(parts.Constructor):
    def __init__(self):
        super().__init__(ParserForSingleLineUsingStandardSyntax(),
                         parts.UnconditionallySuccessfulValidator,
                         Executor)


class Executor(CommandExecutor):
    def __init__(self,
                 environment: InstructionEnvironmentForPreSdsStep,
                 command_line: str):
        self.command_line = command_line

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        return Command(self.command_line, shell=True)
