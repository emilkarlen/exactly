import pathlib

from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntaxSplitAccordingToShellSyntax
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import CommandExecutor
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.process_execution.os_process_execution import Command

SHELL_COMMAND_MARKER = '$'


def act_phase_setup() -> ActPhaseSetup:
    return ActPhaseSetup(Constructor())


class Constructor(parts.Constructor):
    def __init__(self):
        super().__init__(ParserForSingleLineUsingStandardSyntaxSplitAccordingToShellSyntax(),
                         Validator,
                         Executor)


class Validator(parts.Validator):
    def __init__(self,
                 environment: InstructionEnvironmentForPreSdsStep,
                 cmd_and_args: list):
        self.cmd_and_args = cmd_and_args

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        cmd = self.cmd_and_args[0]
        cmd_path = pathlib.Path(cmd)
        if cmd_path.is_absolute():
            if not cmd_path.exists():
                return svh.new_svh_validation_error('File does not exist: ' + cmd)
        else:
            cmd_abs_path = environment.home_directory / cmd
            if not cmd_abs_path.exists():
                return svh.new_svh_validation_error('Not a file relative home-dir: ' + str(cmd_abs_path))
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class Executor(CommandExecutor):
    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep,
                 cmd_and_args: list):
        super().__init__(os_process_executor)
        self.cmd_and_args = cmd_and_args

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        cmd = self.cmd_and_args[0]
        cmd_path = pathlib.Path(cmd)
        if not cmd_path.is_absolute():
            cmd_path = environment.home_directory / cmd_path
            self.cmd_and_args[0] = str(cmd_path)
        return Command(self.cmd_and_args, shell=False)
