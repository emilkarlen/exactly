from symtable import SymbolTable
from typing import Sequence

from exactly_lib.actors.common import relativity_configuration_of_action_to_check, SHELL_COMMAND_MARKER
from exactly_lib.actors.util.executor_made_of_parts import parts
from exactly_lib.actors.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.actors.util.executor_made_of_parts.parts import ExecutableObjectParser, \
    ValidatorFromPreOrPostSdsValidator
from exactly_lib.actors.util.executor_made_of_parts.sub_process_executor import \
    CommandResolverExecutor
from exactly_lib.definitions.test_case.actors import command_line as texts
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.symbol.sdv_validation import SdvValidatorFromDdvValidator
from exactly_lib.test_case.actor import AtcOsProcessExecutor, ParseException, Actor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.parse.parse_list import parse_list
from exactly_lib.test_case_utils.parse.parse_path import parse_path_from_parse_source
from exactly_lib.test_case_utils.program.command import command_sdvs


def actor() -> Actor:
    return parts.ActorFromParts(
        _Parser(),
        _TheValidatorConstructor(),
        _TheExecutorConstructor(),
    )


RELATIVITY_CONFIGURATION = relativity_configuration_of_action_to_check(texts.EXECUTABLE)


class CommandConfiguration(SymbolUser):
    def __init__(self, command_sdv: CommandSdv):
        self._command_sdv = command_sdv

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._command_sdv.references

    def validator(self) -> parts.Validator:
        def get_validator(symbols: SymbolTable) -> DdvValidator:
            return ddv_validators.all_of(self._command_sdv.resolve(symbols).validators)

        return ValidatorFromPreOrPostSdsValidator(
            SdvValidatorFromDdvValidator(get_validator)
        )

    def executor(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 os_process_executor: AtcOsProcessExecutor,
                 ) -> parts.Executor:
        return CommandResolverExecutor(os_process_executor,
                                       self._command_sdv)


class _Parser(ExecutableObjectParser):
    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> CommandConfiguration:
        single_line_parser = ParserForSingleLineUsingStandardSyntax()
        single_line = single_line_parser.apply(instructions)
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
            raise ParseException(svh.new_svh_validation_error__str(msg))
        arg_sdv = parse_string.string_sdv_from_string(striped_argument)
        command_sdv = command_sdvs.for_shell(arg_sdv)
        return CommandConfiguration(command_sdv)

    @staticmethod
    def _parse_executable_file(argument: str) -> CommandConfiguration:
        try:
            source = ParseSource(argument)
            executable = parse_path_from_parse_source(source,
                                                      RELATIVITY_CONFIGURATION)
            arguments = parse_list(source)
            command_sdv = command_sdvs.for_executable_file(executable)
            executable_file = command_sdv.new_with_additional_argument_list(arguments)
            return CommandConfiguration(executable_file)
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException(svh.new_svh_validation_error__str(ex.error_message))


class _TheValidatorConstructor(parts.ValidatorConstructor[CommandConfiguration]):
    def construct(self,
                  environment: InstructionEnvironmentForPreSdsStep,
                  command_configuration: CommandConfiguration,
                  ) -> parts.Validator:
        return command_configuration.validator()


class _TheExecutorConstructor(parts.ExecutorConstructor[CommandConfiguration]):
    def construct(self,
                  os_process_executor: AtcOsProcessExecutor,
                  environment: InstructionEnvironmentForPostSdsStep,
                  command_configuration: CommandConfiguration,
                  ) -> parts.Executor:
        return command_configuration.executor(os_process_executor, environment)
