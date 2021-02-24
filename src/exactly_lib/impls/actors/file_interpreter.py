from typing import Sequence, TypeVar, Callable

from exactly_lib.definitions.test_case import actor as help_texts
from exactly_lib.impls import file_properties
from exactly_lib.impls.actors.common import relativity_configuration_of_action_to_check
from exactly_lib.impls.actors.util import atc_proc_exe_settings
from exactly_lib.impls.actors.util import std_files
from exactly_lib.impls.actors.util.actor_from_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.impls.instructions.utils.logic_type_resolving_helper import full_resolving_env_for_instruction_env
from exactly_lib.impls.types.path import parse_path
from exactly_lib.impls.types.path.path_check import PathCheckValidator, PathCheck
from exactly_lib.impls.types.program.parse import parse_arguments
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import \
    std_error_message_text_for_token_syntax_error_from_exception
from exactly_lib.section_document.element_parsers.token_stream import TokenSyntaxError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.actor import ParseException, Actor, ActionToCheck
from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import sh, svh, eh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.symbol_table import SymbolTable

RELATIVITY_CONFIGURATION = relativity_configuration_of_action_to_check(help_texts.FILE)


def actor(interpreter: CommandSdv) -> Actor:
    return _Actor(interpreter)


class _SourceInfoForInterpreterWithArgumentList:
    def __init__(self,
                 file_name: PathSdv,
                 arguments: ArgumentsSdv):
        self.path = file_name
        self.arguments = arguments

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return tuple(self.path.references) + tuple(self.arguments.references)


class _Actor(Actor):
    def __init__(self, interpreter: CommandSdv):
        self._interpreter = interpreter

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        info = _Parsing(instructions).parse()
        symbol_usages = tuple(self._interpreter.references) + tuple(info.symbol_usages())

        def make_command(environment: FullResolvingEnvironment) -> Command:
            interpreter_command = (self._interpreter.resolve(environment.symbols)
                                   .value_of_any_dependency(environment.tcds))
            source_file_path = info.path.resolve(environment.symbols).value_of_any_dependency(environment.tcds)
            arguments = []
            arguments += interpreter_command.arguments
            arguments.append(str(source_file_path))
            arguments += info.arguments.resolve(environment.symbols).value_of_any_dependency(environment.tcds)
            return Command(interpreter_command.driver, arguments)

        def get_interpreter_and_args_validator(symbols: SymbolTable) -> DdvValidator:
            return ddv_validators.all_of(
                tuple(self._interpreter.resolve(symbols).validators) +
                tuple(info.arguments.resolve(symbols).validators)
            )

        interpreter_and_args_validator = sdv_validation.SdvValidatorFromDdvValidator(get_interpreter_and_args_validator)

        return _ActionToCheck(symbol_usages,
                              interpreter_and_args_validator,
                              info.path,
                              make_command)


class _ActionToCheck(ActionToCheck):
    def __init__(self,
                 symbol_usages: Sequence[SymbolUsage],
                 interpreter_and_args_validator: SdvValidator,
                 source_file: PathSdv,
                 make_command: Callable[[FullResolvingEnvironment], Command],
                 ):
        self._symbol_usages = symbol_usages
        self._source_file = source_file
        self._make_command = make_command

        self._validator = sdv_validation.all_of([
            interpreter_and_args_validator,
            PathCheckValidator(
                PathCheck(source_file,
                          file_properties.must_exist_as(file_properties.FileType.REGULAR))
            ),
        ])

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbol_usages

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep,
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        mb_failure_msg = self._validator.validate_pre_sds_if_applicable(
            environment.path_resolving_environment)
        return svh.new_maybe_svh_validation_error(mb_failure_msg)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        mb_failure_msg = self._validator.validate_post_sds_if_applicable(
            environment.path_resolving_environment)
        return svh.new_maybe_svh_hard_error(mb_failure_msg)

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                ) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                atc_input: AtcExecutionInput,
                output: StdOutputFiles,
                ) -> ExitCodeOrHardError:
        resolving_environment = full_resolving_env_for_instruction_env(os_services, environment)
        try:
            command = self._make_command(resolving_environment)
            settings = atc_proc_exe_settings.for_atc(environment, atc_input)
            with std_files.of_optional_stdin(atc_input.stdin, output) as std_files_:
                exit_code = os_services.command_executor.execute(command, settings, std_files_)
            return eh.new_eh_exit_code(exit_code)
        except HardErrorException as ex:
            return eh.new_eh_hard_error(FailureDetails.new_message(ex.error))


T = TypeVar('T')


class _Parsing:
    def __init__(self, instructions: Sequence[ActPhaseInstruction]):
        self.instructions = instructions
        single_line_parser = ParserForSingleLineUsingStandardSyntax()
        single_line = single_line_parser.apply(instructions)
        single_line = single_line.strip()
        self._source = ParseSource(single_line)
        self._path_parser = parse_path.PathParser(RELATIVITY_CONFIGURATION)

    def parse(self) -> _SourceInfoForInterpreterWithArgumentList:
        try:
            return self._parse_program_with_arguments()
        except TokenSyntaxError as ex:
            raise ParseException.of_str(
                std_error_message_text_for_token_syntax_error_from_exception(ex)
            )
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException.of_str(ex.error_message)

    def _parse_path(self) -> PathSdv:
        return self._path_parser.parse(self._source)

    def _parse_program_with_arguments(self) -> _SourceInfoForInterpreterWithArgumentList:
        source_file = self._parse_path()
        arguments = parse_arguments.parser().parse(self._source)
        return _SourceInfoForInterpreterWithArgumentList(source_file,
                                                         arguments)
