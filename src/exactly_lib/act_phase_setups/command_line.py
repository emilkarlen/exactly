import pathlib

from exactly_lib.act_phase_setups.common import relativity_configuration_of_action_to_check, SHELL_COMMAND_MARKER
from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parts import Parser
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import CommandExecutor
from exactly_lib.help_texts.test_case.actors import command_line as texts
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor, ActPhaseHandling, ParseException
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, SymbolUser
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.parse.parse_file_ref import parse_file_ref_from_parse_source
from exactly_lib.test_case_utils.parse.parse_list import parse_list
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator, \
    PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.test_case_utils.sub_proc.executable_file import ExecutableFile
from exactly_lib.util.process_execution.os_process_execution import Command


def act_phase_setup() -> ActPhaseSetup:
    return ActPhaseSetup(Constructor())


def act_phase_handling() -> ActPhaseHandling:
    return ActPhaseHandling(Constructor())


RELATIVITY_CONFIGURATION = relativity_configuration_of_action_to_check(texts.EXECUTABLE)


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
                 executable_file: ExecutableFile):
        self.executable_file = executable_file

    def symbol_usages(self) -> list:
        return self.executable_file.symbol_usages

    def validator(self, environment: InstructionEnvironmentForPreSdsStep) -> parts.Validator:
        return _ExecutableFileValidator(self.executable_file.validator)

    def executor(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep) -> parts.Executor:
        return _ExecutableFileExecutor(os_process_executor,
                                       self.executable_file)


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
            msg = SHELL_COMMAND_MARKER + ': {COMMAND} string is missing.'.format(
                COMMAND=texts.COMMAND)
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
            executable_file = ExecutableFile(executable_resolver, arguments_resolver)
            return CommandConfigurationForExecutableFile(executable_file)
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException(svh.new_svh_validation_error(ex.error_message))


def _validator(environment: InstructionEnvironmentForPreSdsStep,
               command_info: CommandConfiguration) -> parts.Validator:
    return command_info.validator(environment)


def _executor(os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              command_info: CommandConfiguration) -> parts.Executor:
    return command_info.executor(os_process_executor, environment)


class _ExecutableFileValidator(parts.Validator):
    def __init__(self, validator_that_must_validate_pre_sds: PreOrPostSdsValidator):
        self.validator = PreOrPostSdsSvhValidationErrorValidator(validator_that_must_validate_pre_sds)

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        env = environment.path_resolving_environment
        return self.validator.validate_pre_sds_if_applicable(env)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class _ExecutableFileExecutor(CommandExecutor):
    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 executable_file: ExecutableFile):
        super().__init__(os_process_executor)
        self.executable_file = executable_file

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        return self.executable_file.non_shell_command(environment.path_resolving_environment_pre_or_post_sds)


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
