from typing import Sequence

from exactly_lib.act_phase_setups.common import relativity_configuration_of_action_to_check, SHELL_COMMAND_MARKER
from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.act_phase_setups.util.executor_made_of_parts.parts import Parser
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import \
    CommandResolverExecutor
from exactly_lib.help_texts.test_case.actors import command_line as texts
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor, ActPhaseHandling, ParseException
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, SymbolUser
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.parse.parse_file_ref import parse_file_ref_from_parse_source
from exactly_lib.test_case_utils.parse.parse_list import parse_list
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator, \
    PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.test_case_utils.program.command import command_resolvers
from exactly_lib.test_case_utils.program.command.command_resolver import CommandResolver
from exactly_lib.test_case_utils.program.executable_file import ExecutableFileWithArgsResolver


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
    def __init__(self,
                 command_resolver: CommandResolver,
                 validator: parts.Validator,
                 ):
        self._validator = validator
        self._command_resolver = command_resolver

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._command_resolver.references

    def validator(self) -> parts.Validator:
        return self._validator

    def executor(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep) -> parts.Executor:
        return CommandResolverExecutor(os_process_executor,
                                       self._command_resolver)


class _Parser(Parser):
    def apply(self, act_phase_instructions: Sequence[ActPhaseInstruction]) -> CommandConfiguration:
        single_line_parser = ParserForSingleLineUsingStandardSyntax()
        single_line = single_line_parser.apply(act_phase_instructions)
        single_line = single_line.strip()
        if single_line.startswith(SHELL_COMMAND_MARKER):
            return self._parse_shell_command(single_line[len(SHELL_COMMAND_MARKER):])
        else:
            return self._parse_executable_file(single_line)

    @staticmethod
    def _parse_shell_command(argument: str) -> CommandConfiguration:
        striped_argument = argument.strip()
        if not striped_argument:
            msg = SHELL_COMMAND_MARKER + ': {COMMAND} string is missing.'.format(
                COMMAND=texts.COMMAND)
            raise ParseException(svh.new_svh_validation_error(msg))
        arg_resolver = parse_string.string_resolver_from_string(striped_argument)
        args_as_list = list_resolvers.from_string(arg_resolver)
        command_resolver = command_resolvers.for_shell().new_with_additional_arguments(args_as_list)
        return CommandConfiguration(command_resolver, parts.UnconditionallySuccessfulValidator())

    @staticmethod
    def _parse_executable_file(argument: str) -> CommandConfiguration:
        try:
            source = ParseSource(argument)
            executable_resolver = parse_file_ref_from_parse_source(source,
                                                                   RELATIVITY_CONFIGURATION)
            arguments_resolver = parse_list(source)
            executable_file = ExecutableFileWithArgsResolver(executable_resolver, arguments_resolver)
            return CommandConfiguration(executable_file,
                                        _ExecutableFileValidator(executable_file.validator))
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException(svh.new_svh_validation_error(ex.error_message))


def _validator(environment: InstructionEnvironmentForPreSdsStep,
               command_configuration: CommandConfiguration) -> parts.Validator:
    return command_configuration.validator()


def _executor(os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              command_configuration: CommandConfiguration) -> parts.Executor:
    return command_configuration.executor(os_process_executor, environment)


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
