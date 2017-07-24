import pathlib

from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parts import Parser
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import CommandExecutor
from exactly_lib.instructions.utils.arg_parse import parse_string
from exactly_lib.instructions.utils.arg_parse.parse_file_ref import parse_file_ref_from_parse_source
from exactly_lib.instructions.utils.arg_parse.parse_list import parse_list
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.list_resolver import ListResolver
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor, ActPhaseHandling, ParseException
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, SymbolUser
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.util.process_execution.os_process_execution import Command

SHELL_COMMAND_MARKER = '$'


def act_phase_setup() -> ActPhaseSetup:
    return ActPhaseSetup(Constructor())


def act_phase_handling() -> ActPhaseHandling:
    return ActPhaseHandling(Constructor())


RELATIVITY_CONFIGURATION = RelOptionArgumentConfiguration(
    RelOptionsConfiguration(
        PathRelativityVariants({RelOptionType.REL_HOME},
                               absolute=True),
        is_rel_symbol_option_accepted=False,
        default_option=RelOptionType.REL_HOME),
    argument_syntax_name='EXECUTABLE',
    path_suffix_is_required=True
)


class Constructor(parts.Constructor):
    def __init__(self):
        super().__init__(_Parser(),
                         _validator,
                         _executor)


class CommandConfiguration(SymbolUser):
    def validator(self, environment: InstructionEnvironmentForPreSdsStep) -> parts.Validator:
        raise NotImplementedError()

    def executor(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep) -> parts.Executor:
        raise NotImplementedError()


class CommandConfigurationForShell(CommandConfiguration):
    def __init__(self, command_line_resolver: StringResolver):
        self._command_line_resolver = command_line_resolver

    def symbol_usages(self) -> list:
        return self._command_line_resolver.references

    def validator(self, environment: InstructionEnvironmentForPreSdsStep) -> parts.Validator:
        return parts.UnconditionallySuccessfulValidator()

    def executor(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep) -> parts.Executor:
        return _ShellCommandExecutor(os_process_executor,
                                     self._command_line_resolver)


class CommandConfigurationForExecutableFile(CommandConfiguration):
    def __init__(self,
                 executable: FileRefResolver,
                 arguments: ListResolver):
        self.executable = executable
        self.arguments = arguments

    def symbol_usages(self) -> list:
        return self.executable.references + self.arguments.references

    def validator(self, environment: InstructionEnvironmentForPreSdsStep) -> parts.Validator:
        return _ExecutableFileValidator(self.executable)

    def executor(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep) -> parts.Executor:
        return _ExecutableFileExecutor(os_process_executor,
                                       self.executable,
                                       self.arguments)


class _Parser(Parser):
    def apply(self, act_phase_instructions: list) -> CommandConfiguration:
        single_line_parser = ParserForSingleLineUsingStandardSyntax()
        single_line = single_line_parser.apply(act_phase_instructions)
        single_line = single_line.strip()
        if single_line.startswith(SHELL_COMMAND_MARKER):
            return self._parse_shell_command(single_line[len(SHELL_COMMAND_MARKER):])
        else:
            return self._parse_executable_file(single_line)

    @staticmethod
    def _parse_shell_command(argument: str) -> CommandConfigurationForShell:
        striped_argument = argument.strip()
        if not striped_argument:
            msg = SHELL_COMMAND_MARKER + ': command string is missing.'
            raise ParseException(svh.new_svh_validation_error(msg))
        arg_resolver = parse_string.string_resolver_from_string(striped_argument)
        return CommandConfigurationForShell(arg_resolver)

    @staticmethod
    def _parse_executable_file(argument: str) -> CommandConfigurationForExecutableFile:
        try:
            source = ParseSource(argument)
            executable_resolver = parse_file_ref_from_parse_source(source,
                                                                   RELATIVITY_CONFIGURATION)
            arguments_resolver = parse_list(source)
            return CommandConfigurationForExecutableFile(executable_resolver, arguments_resolver)
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException(svh.new_svh_validation_error(ex.error_message))


# def _cmd(cmd: str) -> FileRefResolver:
#     cmd_path = pathlib.Path(cmd)
#     if cmd_path.is_absolute():
#         file_ref = file_refs.absolute_file_name(cmd)
#     else:
#         file_ref = file_refs.rel_home(PathPartAsFixedPath(cmd))
#     return FileRefConstant(file_ref)


def _validator(environment: InstructionEnvironmentForPreSdsStep,
               command_info: CommandConfiguration) -> parts.Validator:
    return command_info.validator(environment)


def _executor(os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              command_info: CommandConfiguration) -> parts.Executor:
    return command_info.executor(os_process_executor, environment)


class _ExecutableFileValidator(parts.Validator):
    def __init__(self, executable: FileRefResolver):
        self.executable = executable

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        cmd_path = self.executable.resolve(environment.symbols).value_pre_sds(environment.home_directory)
        if not cmd_path.exists():
            return svh.new_svh_validation_error('File does not exist: ' + str(cmd_path))
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class _ExecutableFileExecutor(CommandExecutor):
    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 executable: FileRefResolver,
                 arguments: ListResolver):
        super().__init__(os_process_executor)
        self.executable = executable
        self.arguments = arguments

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds

        cmd_path = self.executable.resolve_value_of_any_dependency(path_resolving_env)
        cmd_and_args = [str(cmd_path)]
        cmd_and_args.extend(self.arguments.resolve_value_of_any_dependency(path_resolving_env))

        return Command(cmd_and_args,
                       shell=False)


class _ShellCommandExecutor(CommandExecutor):
    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 command_line_resolver: StringResolver):
        super().__init__(os_process_executor)
        self._command_line_resolver = command_line_resolver

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        command_line = self._command_line_resolver.resolve_value_of_any_dependency(
            environment.path_resolving_environment_pre_or_post_sds)
        return Command(command_line,
                       shell=True)
