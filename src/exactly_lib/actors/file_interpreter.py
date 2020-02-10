import pathlib
import shlex
from typing import Sequence, List, TypeVar, Callable

from exactly_lib.actors.common import relativity_configuration_of_action_to_check
from exactly_lib.actors.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.definitions.test_case.actors import file_interpreter as texts
from exactly_lib.instructions.utils.data_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import \
    std_error_message_text_for_token_syntax_error_from_exception
from exactly_lib.section_document.element_parsers.token_stream import TokenSyntaxError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.resolving_helper import DataTypeResolvingHelper
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.actor import AtcOsProcessExecutor, ParseException, Actor, ActionToCheck
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import svh, sh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.parse import parse_string, parse_path, parse_list
from exactly_lib.test_case_utils.path_check import PathCheckValidator, PathCheck
from exactly_lib.type_system.logic.program.process_execution import commands
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.std import StdFiles

RELATIVITY_CONFIGURATION = relativity_configuration_of_action_to_check(texts.FILE)


def actor(interpreter: Command) -> Actor:
    return _ActorConstructor(interpreter.arguments).visit(interpreter.driver)


class _SourceInfoForInterpreterWithArgumentList:
    def __init__(self,
                 file_name: PathSdv,
                 arguments: ListSdv):
        self.path = file_name
        self.arguments = arguments

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return tuple(self.path.references) + tuple(self.arguments.references)


class _SourceInfoForInterpreterThatIsAShellCommand:
    def __init__(self,
                 file_name: PathSdv,
                 arguments: StringSdv):
        self.path = file_name
        self.arguments = arguments

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return tuple(self.path.references) + tuple(self.arguments.references)


class _ActorForInterpreterCommandWithArguments(Actor):
    def __init__(self,
                 interpreter: commands.CommandDriverWithArgumentList,
                 interpreter_arguments: List[str],
                 ):
        self._interpreter = interpreter
        self._interpreter_arguments = interpreter_arguments

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        info = _Parsing(instructions).program_with_arguments()

        def make_command(resolver: DataTypeResolvingHelper) -> Command:
            arguments = []
            arguments += self._interpreter_arguments
            arguments.append(str(resolver.path(info.path).primitive))
            arguments += resolver.list(info.arguments)
            return Command(self._interpreter, arguments)

        return _ActionToCheck(info.symbol_usages(),
                              info.path,
                              make_command)


class _ActorForInterpreterThatIsAShellCommand(Actor):
    def __init__(self, interpreter: commands.CommandDriverForShell):
        self._interpreter = interpreter

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        info = _Parsing(instructions).shell()

        def make_command(resolver: DataTypeResolvingHelper) -> Command:
            arguments = [shlex.quote(str(resolver.path(info.path).primitive)),
                         resolver.string(info.arguments)]

            return Command(self._interpreter, arguments)

        return _ActionToCheck(info.symbol_usages(),
                              info.path,
                              make_command)


class _ActionToCheck(ActionToCheck):
    def __init__(self,
                 symbols: Sequence[SymbolUsage],
                 source_file: PathSdv,
                 make_command: Callable[[DataTypeResolvingHelper], Command],
                 ):
        self._symbols = symbols
        self._source_file = source_file
        self._make_command = make_command
        self._validator = PathCheckValidator(PathCheck(source_file,
                                                       file_properties.must_exist_as(file_properties.FileType.REGULAR)))

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbols

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep,
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        mb_failure_msg = self._validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)
        return svh.new_maybe_svh_validation_error(mb_failure_msg)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        mb_failure_msg = self._validator.validate_post_sds_if_applicable(environment.path_resolving_environment)
        return svh.new_maybe_svh_hard_error(mb_failure_msg)

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles,
                ) -> ExitCodeOrHardError:
        command = self._make_command(resolving_helper_for_instruction_env(environment))
        return os_process_executor.execute(command, std_files, environment.process_execution_settings)


T = TypeVar('T')


class _Parsing:
    def __init__(self, instructions: Sequence[ActPhaseInstruction]):
        self.instructions = instructions
        single_line_parser = ParserForSingleLineUsingStandardSyntax()
        single_line = single_line_parser.apply(instructions)
        single_line = single_line.strip()
        self._source = ParseSource(single_line)

    def program_with_arguments(self) -> _SourceInfoForInterpreterWithArgumentList:
        return self._parse(self._parse_program_with_arguments)

    def shell(self) -> _SourceInfoForInterpreterThatIsAShellCommand:
        return self._parse(self._parse_shell)

    @staticmethod
    def _parse(parser: Callable[[], T]) -> T:
        try:
            return parser()
        except TokenSyntaxError as ex:
            raise ParseException(
                svh.new_svh_validation_error__str(std_error_message_text_for_token_syntax_error_from_exception(ex)))
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException(svh.new_svh_validation_error__str(ex.error_message))

    def _parse_path(self) -> PathSdv:
        return parse_path.parse_path_from_parse_source(self._source,
                                                       RELATIVITY_CONFIGURATION)

    def _parse_program_with_arguments(self) -> _SourceInfoForInterpreterWithArgumentList:
        source_file = self._parse_path()
        arguments = parse_list.parse_list(self._source)
        return _SourceInfoForInterpreterWithArgumentList(source_file,
                                                         arguments)

    def _parse_shell(self) -> _SourceInfoForInterpreterThatIsAShellCommand:
        source_file = self._parse_path()
        stripped_arguments_string = self._source.remaining_source.strip()
        arg_sdv = parse_string.string_sdv_from_string(stripped_arguments_string)
        return _SourceInfoForInterpreterThatIsAShellCommand(source_file,
                                                            arg_sdv)


class _ActorConstructor(commands.CommandDriverArgumentTypePseudoVisitor[Actor]):
    def __init__(self, arguments: List[str]):
        self.arguments = arguments

    def visit_shell(self, driver: commands.CommandDriverForShell) -> Actor:
        return _ActorForInterpreterThatIsAShellCommand(driver)

    def visit_with_argument_list(self, driver: commands.CommandDriverWithArgumentList) -> Actor:
        return _ActorForInterpreterCommandWithArguments(driver, self.arguments)
