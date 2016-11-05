import pathlib

from exactly_lib.act_phase_setups import utils
from exactly_lib.act_phase_setups.util.executor_made_of_parts import main as executor_made_of_parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.execution.act_phase import ExitCodeOrHardError
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.phases.common import HomeAndSds, InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.std import StdFiles


def act_phase_setup() -> ActPhaseSetup:
    return ActPhaseSetup(Constructor())


class Constructor(executor_made_of_parts.Constructor):
    def __init__(self):
        super().__init__(ParserForSingleLineUsingStandardSyntax(),
                         executor_made_of_parts.UnconditionallySuccessfulValidator,
                         Executor)


class Executor(executor_made_of_parts.Executor):
    def __init__(self,
                 environment: InstructionEnvironmentForPreSdsStep,
                 command_line: str):
        self.environment = environment
        self.command_line = command_line

    def prepare(self, home_and_sds: HomeAndSds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def execute(self, home_and_sds: HomeAndSds, script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return utils.execute_shell_command(self.command_line,
                                           std_files,
                                           timeout=self.environment.timeout_in_seconds)
