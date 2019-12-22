import functools
import pathlib
import shlex
from typing import Sequence, List

from exactly_lib.actors.common import relativity_configuration_of_action_to_check
from exactly_lib.actors.util.executor_made_of_parts import parts
from exactly_lib.actors.util.executor_made_of_parts.parser_for_single_line import \
    ParserForSingleLineUsingStandardSyntax
from exactly_lib.actors.util.executor_made_of_parts.parts import ExecutableObjectParser
from exactly_lib.actors.util.executor_made_of_parts.sub_process_executor import \
    SubProcessExecutor
from exactly_lib.definitions.test_case.actors import file_interpreter as texts
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import \
    std_error_message_text_for_token_syntax_error_from_exception
from exactly_lib.section_document.element_parsers.token_stream import TokenSyntaxError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import list_sdvs
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.actor import AtcOsProcessExecutor, ParseException, Actor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, SymbolUser
from exactly_lib.test_case.result import svh
from exactly_lib.test_case.validation.sdv_validation import PreOrPostSdsSvhValidationErrorValidator
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.parse import parse_string, parse_path, parse_list
from exactly_lib.test_case_utils.path_check import PathCheckValidator, PathCheck
from exactly_lib.test_case_utils.program.command import command_sdvs
from exactly_lib.type_system.logic.program.process_execution import commands
from exactly_lib.type_system.logic.program.process_execution.command import Command, ProgramAndArguments

RELATIVITY_CONFIGURATION = relativity_configuration_of_action_to_check(texts.FILE)


def actor(interpreter: Command) -> Actor:
    return _CommandTranslator(interpreter.arguments).visit(interpreter.driver)


class ActorForInterpreterThatIsAnExecutableFile(parts.ActorFromParts):
    def __init__(self, pgm_and_args: ProgramAndArguments):
        super().__init__(_Parser(is_shell=False),
                         _Validator,
                         functools.partial(_ProgramExecutor, pgm_and_args))


class ActorForInterpreterThatIsAShellCommand(parts.ActorFromParts):
    def __init__(self, shell_command_line: str):
        super().__init__(_Parser(is_shell=True),
                         _Validator,
                         functools.partial(_ShellSubProcessExecutor, shell_command_line))


class _SourceInfo(SymbolUser):
    def __init__(self, file_name: PathSdv):
        self.path = file_name


class _SourceInfoForInterpreterThatIsAnExecutableFile(_SourceInfo):
    def __init__(self,
                 file_name: PathSdv,
                 arguments: ListSdv):
        super().__init__(file_name)
        self.arguments = arguments

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return tuple(self.path.references) + tuple(self.arguments.references)


class _SourceInfoForInterpreterThatIsAShellCommand(_SourceInfo):
    def __init__(self,
                 file_name: PathSdv,
                 arguments: StringSdv):
        super().__init__(file_name)
        self.arguments = arguments

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return tuple(self.path.references) + tuple(self.arguments.references)


class _Parser(ExecutableObjectParser):
    def __init__(self, is_shell: bool):
        self.is_shell = is_shell

    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> _SourceInfo:
        single_line_parser = ParserForSingleLineUsingStandardSyntax()
        single_line = single_line_parser.apply(instructions)
        single_line = single_line.strip()
        source = ParseSource(single_line)
        try:
            source_file_sdv = parse_path.parse_path_from_parse_source(source,
                                                                      RELATIVITY_CONFIGURATION)
            if self.is_shell:
                return self._shell(source_file_sdv, source)
            else:
                return self._executable_file(source_file_sdv, source)
        except TokenSyntaxError as ex:
            raise ParseException(
                svh.new_svh_validation_error__str(std_error_message_text_for_token_syntax_error_from_exception(ex)))
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException(svh.new_svh_validation_error__str(ex.error_message))

    @staticmethod
    def _executable_file(source_file: PathSdv,
                         source: ParseSource,
                         ) -> _SourceInfoForInterpreterThatIsAnExecutableFile:
        arguments = parse_list.parse_list(source)
        return _SourceInfoForInterpreterThatIsAnExecutableFile(source_file,
                                                               arguments)

    @staticmethod
    def _shell(source_file: PathSdv,
               source: ParseSource,
               ) -> _SourceInfoForInterpreterThatIsAShellCommand:
        stripped_arguments_string = source.remaining_source.strip()
        arg_sdv = parse_string.string_sdv_from_string(stripped_arguments_string)
        return _SourceInfoForInterpreterThatIsAShellCommand(source_file,
                                                            arg_sdv)


class _Validator(parts.Validator):
    def __init__(self,
                 environment: InstructionEnvironmentForPreSdsStep,
                 source: _SourceInfo):
        self.environment = environment
        self.source = source
        self.validator = PreOrPostSdsSvhValidationErrorValidator(
            PathCheckValidator(PathCheck(source.path,
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


class _ProgramExecutor(SubProcessExecutor):
    def __init__(self,
                 interpreter: ProgramAndArguments,
                 os_process_executor: AtcOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep,
                 source: _SourceInfoForInterpreterThatIsAnExecutableFile):
        super().__init__(os_process_executor)
        self.interpreter = interpreter
        self.source = source

    def _command_to_execute(self, script_output_dir_path: pathlib.Path) -> CommandSdv:
        arguments = list_sdvs.concat([
            list_sdvs.from_strings([string_sdvs.from_path_sdv(self.source.path)]),
            self.source.arguments,
        ])

        return (command_sdvs
                .from_program_and_arguments(self.interpreter)
                .new_with_additional_argument_list(arguments)
                )


class _ShellSubProcessExecutor(SubProcessExecutor):
    def __init__(self,
                 shell_command_of_interpreter: str,
                 os_process_executor: AtcOsProcessExecutor,
                 environment: InstructionEnvironmentForPreSdsStep,
                 source: _SourceInfoForInterpreterThatIsAShellCommand):
        super().__init__(os_process_executor)
        self.shell_command_of_interpreter = shell_command_of_interpreter
        self.source = source

    def _command_to_execute(self, script_output_dir_path: pathlib.Path) -> CommandSdv:
        command_line_elements = list_sdvs.from_strings([
            string_sdvs.str_constant(self.shell_command_of_interpreter),

            string_sdvs.from_fragments([
                string_sdvs.transformed_fragment(
                    string_sdvs.path_fragment(self.source.path),
                    shlex.quote)
            ]),

            self.source.arguments,
        ])
        return command_sdvs.for_shell(string_sdvs.from_list_sdv(command_line_elements))


class _CommandTranslator(commands.CommandDriverVisitor):
    def __init__(self, arguments: List[str]):
        self.arguments = arguments

    def visit_shell(self, driver: commands.CommandDriverForShell) -> parts.ActorFromParts:
        return ActorForInterpreterThatIsAShellCommand(driver.shell_command_line_with_args(self.arguments))

    def visit_executable_file(self, driver: commands.CommandDriverForExecutableFile) -> parts.ActorFromParts:
        return ActorForInterpreterThatIsAnExecutableFile(driver.as_program_and_args(self.arguments))

    def visit_system_program(self, driver: commands.CommandDriverForSystemProgram) -> parts.ActorFromParts:
        raise ValueError('Unsupported interpreter: System Program Command')
