import functools
import pathlib
import shlex

from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parts import Parser
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import CommandExecutor
from exactly_lib.instructions.utils.arg_parse.parse_utils import TokenStream
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor, ActPhaseHandling
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.process_execution.os_process_execution import Command

SHELL_COMMAND_MARKER = '$'


def act_phase_setup(interpreter: Command) -> ActPhaseSetup:
    return ActPhaseSetup(constructor(interpreter))


def act_phase_handling(interpreter: Command) -> ActPhaseHandling:
    return ActPhaseHandling(constructor(interpreter))


def constructor(interpreter: Command) -> parts.Constructor:
    if interpreter.shell:
        return ConstructorForShellCommand(interpreter.args)
    else:
        return ConstructorForExecutableFile(interpreter.args)


class ConstructorForExecutableFile(parts.Constructor):
    def __init__(self, cmd_and_args: list):
        super().__init__(_Parser(is_shell=False),
                         _Validator,
                         functools.partial(_ExecutableFileExecutor, cmd_and_args))


class ConstructorForShellCommand(parts.Constructor):
    def __init__(self, shell_command: str):
        super().__init__(_Parser(is_shell=True),
                         _Validator,
                         functools.partial(_ShellCommandExecutor, shell_command))


class _SourceInfo:
    def __init__(self,
                 file_name: str,
                 remaining_arguments):
        self.remaining_arguments = remaining_arguments
        self.file_reference = file_name


class _Parser(Parser):
    def __init__(self, is_shell: bool):
        self.is_shell = is_shell

    def apply(self, act_phase_instructions: list) -> _SourceInfo:
        single_line_parser = ParserForSingleLineUsingStandardSyntax()
        single_line = single_line_parser.apply(act_phase_instructions)
        single_line = single_line.strip()
        try:
            token_stream = TokenStream(single_line)
            if token_stream.is_null:
                raise ValueError('Illegal state: cannot read a single token from source: "{}"'.format(single_line))
            remaining_arguments = self._parse_remaining_arguments(token_stream.tail_source)
            return _SourceInfo(token_stream.head, remaining_arguments)
        except Exception as ex:
            raise parts.ParseException(svh.new_svh_validation_error(str(ex)))

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

    def _parse_remaining_arguments(self, tail_source: str):
        if self.is_shell:
            if tail_source is None:
                return None
            return tail_source.strip()
        else:
            if tail_source is None:
                return []
            try:
                return shlex.split(tail_source)
            except Exception as ex:
                raise parts.ParseException(svh.new_svh_validation_error(str(ex)))


class _Validator(parts.Validator):
    def __init__(self,
                 environment: InstructionEnvironmentForPreSdsStep,
                 source: _SourceInfo):
        self.environment = environment
        self.source = source

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        file_path = pathlib.Path(self.source.file_reference)
        if file_path.is_absolute():
            if not file_path.exists():
                return svh.new_svh_validation_error('File does not exist: ' + self.source.file_reference)
        else:
            file_abs_path = self.environment.home_directory / self.source.file_reference
            if not file_abs_path.exists():
                msg = 'Not an existing file relative home-dir: ' + str(file_abs_path)
                return svh.new_svh_validation_error(msg)
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class _ExecutableFileExecutor(CommandExecutor):
    def __init__(self,
                 cmd_and_args_of_interpreter: list,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep,
                 source: _SourceInfo):
        super().__init__(os_process_executor)
        self.cmd_and_args_of_interpreter = cmd_and_args_of_interpreter
        self.source = source

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        absolute_file_name = _resolve_absolute_file_name(self.source.file_reference, environment)
        cmd_and_args = self.cmd_and_args_of_interpreter + [absolute_file_name] + self.source.remaining_arguments
        return Command(cmd_and_args, shell=False)


class _ShellCommandExecutor(CommandExecutor):
    def __init__(self,
                 shell_command_of_interpreter: str,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep,
                 source: _SourceInfo):
        super().__init__(os_process_executor)
        self.shell_command_of_interpreter = shell_command_of_interpreter
        self.source = source

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        return Command(self.command_line, shell=True)


def _resolve_absolute_file_name(file_reference: str, environment: InstructionEnvironmentForPostSdsStep) -> str:
    file_path = pathlib.Path(file_reference)
    if file_path.is_absolute():
        return file_reference
    else:
        file_abs_path = environment.home_directory / file_reference
        return str(file_abs_path)
