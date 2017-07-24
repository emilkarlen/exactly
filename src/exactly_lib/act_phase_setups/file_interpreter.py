import functools
import pathlib
import shlex

from exactly_lib.act_phase_setups.common import relativity_configuration_of_action_to_check
from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parts import Parser
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import CommandExecutor
from exactly_lib.instructions.utils import file_properties
from exactly_lib.instructions.utils.arg_parse.parse_file_ref import parse_file_ref_from_parse_source
from exactly_lib.instructions.utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor, ActPhaseHandling, ParseException
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, SymbolUser
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.process_execution.os_process_execution import Command

SHELL_COMMAND_MARKER = '$'

RELATIVITY_CONFIGURATION = relativity_configuration_of_action_to_check('FILE')


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


class _SourceInfo(SymbolUser):
    def __init__(self,
                 file_name: FileRefResolver,
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
        source = ParseSource(single_line)
        try:
            source_file_resolver = parse_file_ref_from_parse_source(source,
                                                                    RELATIVITY_CONFIGURATION)
            remaining_arguments = self._parse_remaining_arguments(source.remaining_source)
            return _SourceInfo(source_file_resolver, remaining_arguments)
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException(svh.new_svh_validation_error(ex.error_message))
        except Exception as ex:
            raise ParseException(svh.new_svh_validation_error(str(ex)))

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
                raise ParseException(svh.new_svh_validation_error(str(ex)))


class _Validator(parts.Validator):
    def __init__(self,
                 environment: InstructionEnvironmentForPreSdsStep,
                 source: _SourceInfo):
        self.environment = environment
        self.source = source
        self.validator = PreOrPostSdsSvhValidationErrorValidator(
            FileRefCheckValidator(FileRefCheck(source.file_reference,
                                               file_properties.must_exist_as(file_properties.FileType.REGULAR)))
        )

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return self.validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)

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
        src_path = self.source.file_reference.resolve(environment.symbols).value_pre_sds(environment.home_directory)
        cmd_and_args = self.cmd_and_args_of_interpreter + [str(src_path)] + self.source.remaining_arguments
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
        remaining_arguments = '' if not self.source.remaining_arguments else self.source.remaining_arguments
        src_path = self.source.file_reference.resolve(environment.symbols).value_pre_sds(environment.home_directory)
        quoted_absolute_path_to_file = shlex.quote(str(src_path))
        command_string = '{interpreter} {source_file} {command_line_arguments}'.format(
            interpreter=self.shell_command_of_interpreter,
            source_file=quoted_absolute_path_to_file,
            command_line_arguments=remaining_arguments,
        )
        return Command(command_string, shell=True)


def _resolve_absolute_file_name(file_reference: str, environment: InstructionEnvironmentForPostSdsStep) -> str:
    file_path = pathlib.Path(file_reference)
    if file_path.is_absolute():
        return file_reference
    else:
        file_abs_path = environment.home_directory / file_reference
        return str(file_abs_path)
