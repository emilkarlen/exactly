import pathlib
import shlex

from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parts import Parser
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import CommandExecutor
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor, ActPhaseHandling
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.process_execution.os_process_execution import Command

SHELL_COMMAND_MARKER = '$'


def act_phase_setup() -> ActPhaseSetup:
    return ActPhaseSetup(Constructor())


def act_phase_handling() -> ActPhaseHandling:
    return ActPhaseHandling(Constructor())


class Constructor(parts.Constructor):
    def __init__(self):
        super().__init__(_Parser(),
                         _validator,
                         _executor)


class _Parser(Parser):
    def apply(self, act_phase_instructions: list) -> Command:
        single_line_parser = ParserForSingleLineUsingStandardSyntax()
        single_line = single_line_parser.apply(act_phase_instructions)
        single_line = single_line.strip()
        if single_line.startswith(SHELL_COMMAND_MARKER):
            return self._parse_shell_command(single_line[len(SHELL_COMMAND_MARKER):])
        else:
            return self._parse_executable_file(single_line)

    @staticmethod
    def _parse_shell_command(argument: str) -> Command:
        striped_argument = argument.strip()
        if not striped_argument:
            msg = SHELL_COMMAND_MARKER + ': command string is missing.'
            raise parts.ParseException(svh.new_svh_validation_error(msg))
        return Command(striped_argument, shell=True)

    @staticmethod
    def _parse_executable_file(argument: str) -> Command:
        cmd_and_args = shlex.split(argument)
        return Command(cmd_and_args, shell=False)


def _validator(environment: InstructionEnvironmentForPreSdsStep, command: Command) -> parts.Validator:
    if command.shell:
        return parts.UnconditionallySuccessfulValidator()
    else:
        return _ExecutableFileValidator(command.args)


def _executor(os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              command: Command) -> parts.Executor:
    if command.shell:
        return _ShellCommandExecutor(os_process_executor, command.args)
    else:
        return _ExecutableFileExecutor(os_process_executor, command.args)


class _ExecutableFileValidator(parts.Validator):
    def __init__(self, cmd_and_args: list):
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


class _ExecutableFileExecutor(CommandExecutor):
    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
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


class _ShellCommandExecutor(CommandExecutor):
    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 command_line: str):
        super().__init__(os_process_executor)
        self.command_line = command_line

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        return Command(self.command_line, shell=True)
