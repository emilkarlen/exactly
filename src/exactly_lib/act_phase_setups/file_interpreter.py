import functools
import pathlib
import shlex
from copy import copy

from exactly_lib.act_phase_setups.common import relativity_configuration_of_action_to_check
from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parts import Parser
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import CommandExecutor
from exactly_lib.help_texts.test_case.actors import file_interpreter as texts
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import \
    std_error_message_text_for_token_syntax_error_from_exception
from exactly_lib.section_document.element_parsers.token_stream import TokenSyntaxError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor, ActPhaseHandling, ParseException
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, SymbolUser
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from exactly_lib.test_case_utils.parse import parse_string, parse_file_ref, parse_list
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.util.process_execution.os_process_execution import Command

RELATIVITY_CONFIGURATION = relativity_configuration_of_action_to_check(texts.FILE)


def act_phase_setup(interpreter: Command) -> ActPhaseSetup:
    return ActPhaseSetup(constructor(interpreter))


def act_phase_handling(interpreter: Command) -> ActPhaseHandling:
    return ActPhaseHandling(constructor(interpreter))


def constructor(interpreter: Command) -> parts.Constructor:
    if interpreter.shell:
        return ConstructorForInterpreterThatIsAShellCommand(interpreter.args)
    else:
        return ConstructorForInterpreterThatIsAnExecutableFile(interpreter.args)


class ConstructorForInterpreterThatIsAnExecutableFile(parts.Constructor):
    def __init__(self, cmd_and_args: list):
        super().__init__(_Parser(is_shell=False),
                         _Validator,
                         functools.partial(_ExecutableFileExecutor, cmd_and_args))


class ConstructorForInterpreterThatIsAShellCommand(parts.Constructor):
    def __init__(self, shell_command: str):
        super().__init__(_Parser(is_shell=True),
                         _Validator,
                         functools.partial(_ShellCommandExecutor, shell_command))


class _SourceInfo(SymbolUser):
    def __init__(self,
                 file_name: FileRefResolver):
        self.file_reference = file_name


class _SourceInfoForInterpreterThatIsAnExecutableFile(_SourceInfo):
    def __init__(self,
                 file_name: FileRefResolver,
                 arguments: ListResolver):
        super().__init__(file_name)
        self.arguments = arguments

    def symbol_usages(self) -> list:
        return self.file_reference.references + self.arguments.references


class _SourceInfoForInterpreterThatIsAShellCommand(_SourceInfo):
    def __init__(self,
                 file_name: FileRefResolver,
                 arguments: StringResolver):
        super().__init__(file_name)
        self.arguments = arguments

    def symbol_usages(self) -> list:
        return self.file_reference.references + self.arguments.references


class _Parser(Parser):
    def __init__(self, is_shell: bool):
        self.is_shell = is_shell

    def apply(self, act_phase_instructions: list) -> _SourceInfo:
        single_line_parser = ParserForSingleLineUsingStandardSyntax()
        single_line = single_line_parser.apply(act_phase_instructions)
        single_line = single_line.strip()
        source = ParseSource(single_line)
        try:
            source_file_resolver = parse_file_ref.parse_file_ref_from_parse_source(source,
                                                                                   RELATIVITY_CONFIGURATION)
            if self.is_shell:
                return self._shell(source_file_resolver, source)
            else:
                return self._executable_file(source_file_resolver, source)
        except TokenSyntaxError as ex:
            raise ParseException(
                svh.new_svh_validation_error(std_error_message_text_for_token_syntax_error_from_exception(ex)))
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException(svh.new_svh_validation_error(ex.error_message))

    @staticmethod
    def _executable_file(source_file: FileRefResolver,
                         source: ParseSource,
                         ) -> _SourceInfoForInterpreterThatIsAnExecutableFile:
        arguments = parse_list.parse_list(source)
        return _SourceInfoForInterpreterThatIsAnExecutableFile(source_file,
                                                               arguments)

    @staticmethod
    def _shell(source_file: FileRefResolver,
               source: ParseSource,
               ) -> _SourceInfoForInterpreterThatIsAShellCommand:
        stripped_arguments_string = source.remaining_source.strip()
        arg_resolver = parse_string.string_resolver_from_string(stripped_arguments_string)
        return _SourceInfoForInterpreterThatIsAShellCommand(source_file,
                                                            arg_resolver)


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
                 source: _SourceInfoForInterpreterThatIsAnExecutableFile):
        super().__init__(os_process_executor)
        self.cmd_and_args_of_interpreter = cmd_and_args_of_interpreter
        self.source = source

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        cmd_and_args = copy(self.cmd_and_args_of_interpreter)

        src_path = self.source.file_reference.resolve(environment.symbols).value_pre_sds(environment.hds)
        cmd_and_args.append(str(src_path))

        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        args = self.source.arguments.resolve_value_of_any_dependency(path_resolving_env)
        cmd_and_args.extend(args)

        return Command(cmd_and_args, shell=False)


class _ShellCommandExecutor(CommandExecutor):
    def __init__(self,
                 shell_command_of_interpreter: str,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep,
                 source: _SourceInfoForInterpreterThatIsAnExecutableFile):
        super().__init__(os_process_executor)
        self.shell_command_of_interpreter = shell_command_of_interpreter
        self.source = source

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        remaining_arguments = self.source.arguments.resolve_value_of_any_dependency(path_resolving_env)

        src_path = self.source.file_reference.resolve(environment.symbols).value_pre_sds(environment.hds)
        quoted_src_path = shlex.quote(str(src_path))

        command_string = '{interpreter} {source_file} {command_line_arguments}'.format(
            interpreter=self.shell_command_of_interpreter,
            source_file=quoted_src_path,
            command_line_arguments=remaining_arguments,
        )
        return Command(command_string, shell=True)
