import pathlib
from typing import Sequence, Optional

from exactly_lib.common.err_msg import std_err_contents
from exactly_lib.instructions.multi_phase.utils import instruction_embryo
from exactly_lib.instructions.multi_phase.utils.instruction_embryo import \
    InstructionEmbryoParserWoFileSystemLocationInfo
from exactly_lib.instructions.multi_phase.utils.instruction_part_utils import MainStepResultTranslator, \
    PartsParserFromEmbryoParser
from exactly_lib.instructions.multi_phase.utils.instruction_parts import InstructionPartsParser
from exactly_lib.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.section_document.element_parsers import misc_utils
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol import sdv_validation
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.symbol.sdv_validation import SdvValidator
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import pfh, sh
from exactly_lib.test_case_utils.program import top_lvl_error_msg_rendering
from exactly_lib.test_case_utils.program_execution import command_executors
from exactly_lib.test_case_utils.program_execution.command_executor import CommandExecutor
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.util.process_execution import file_ctx_managers, process_output_files
from exactly_lib.util.process_execution.executors.read_stderr_on_error import ResultWithFiles, \
    ExecutorThatStoresResultInFilesInDirAndReadsStderrOnNonZeroExitCode
from exactly_lib.util.process_execution.process_executor import ExecutableExecutor, ProcessExecutor
from exactly_lib.util.process_execution.process_output_files import FileNames


class ExecutionResultAndStderr(tuple):
    """
    Result of an execution of a sub process

    Contents of stderr is included, if exit code is non zero.
    """

    def __new__(cls,
                exit_code: int,
                stderr_contents: Optional[str],
                output_dir_path: pathlib.Path,
                program: StructureRenderer,
                ):
        return tuple.__new__(cls, (exit_code,
                                   stderr_contents,
                                   output_dir_path,
                                   program))

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def stderr_contents(self) -> Optional[str]:
        return self[1]

    @property
    def output_dir_path(self) -> pathlib.Path:
        return self[2]

    @property
    def program(self) -> StructureRenderer:
        return self[3]

    @property
    def file_names(self) -> FileNames:
        return process_output_files.FILE_NAMES

    def path_of(self, output_file: process_output_files.ProcOutputFile) -> pathlib.Path:
        return self.output_dir_path / self.file_names.name_of(output_file)


class TheInstructionEmbryo(instruction_embryo.InstructionEmbryo[ExecutionResultAndStderr]):
    def __init__(self, program: ProgramSdv):
        self._program = program

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._program.references

    @property
    def validator(self) -> SdvValidator:
        return sdv_validation.SdvValidatorFromDdvValidator(
            lambda symbols: self._program.resolve(symbols).validator
        )

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             ) -> ExecutionResultAndStderr:
        resolver = resolving_helper_for_instruction_env(os_services, environment)
        program = resolver.resolve_program(self._program)
        storage_dir = environment.tmp_dir__path_access.root_dir__existing

        command_executor = self._command_executor(
            os_services,
            self._executor(storage_dir)
        )

        result = command_executor.execute(
            environment.proc_exe_settings,
            program.command,
            program.structure(),
        )

        return ExecutionResultAndStderr(
            result.exit_code,
            result.stderr,
            storage_dir,
            program.structure(),
        )

    @staticmethod
    def _command_executor(os_services: OsServices,
                          executor: ExecutableExecutor[ResultWithFiles],
                          ) -> CommandExecutor[ResultWithFiles]:
        return command_executors.executor_that_raises_hard_error(
            os_services,
            executor
        )

    @staticmethod
    def _executor(storage_dir: pathlib.Path) -> ExecutableExecutor[ResultWithFiles]:
        return ExecutorThatStoresResultInFilesInDirAndReadsStderrOnNonZeroExitCode(
            ProcessExecutor(),
            storage_dir,
            file_ctx_managers.dev_null(),
            std_err_contents.STD_ERR_TEXT_READER,
        )


class ResultTranslator(MainStepResultTranslator[ExecutionResultAndStderr]):
    def translate_for_non_assertion(self, main_result: ExecutionResultAndStderr) -> sh.SuccessOrHardError:
        return result_to_sh(main_result)

    def translate_for_assertion(self, main_result: ExecutionResultAndStderr) -> pfh.PassOrFailOrHardError:
        return result_to_pfh(main_result)


class InstructionEmbryoParser(InstructionEmbryoParserWoFileSystemLocationInfo[ExecutionResultAndStderr]):
    def __init__(self,
                 instruction_name: str,
                 program_parser: Parser[ProgramSdv]):
        self.instruction_name = instruction_name
        self.program_parser = program_parser

    def _parse(self, source: ParseSource) -> TheInstructionEmbryo:
        program = self.program_parser.parse(source)

        self._advance_source(source)

        return TheInstructionEmbryo(program)

    @staticmethod
    def _advance_source(source: ParseSource):
        if source.has_current_line:
            if not source.is_at_eol__except_for_space:
                misc_utils.raise_superfluous_arguments(source.remaining_part_of_current_line.strip())
            source.consume_current_line()


def parts_parser(instruction_name: str,
                 program_parser: Parser[ProgramSdv]
                 ) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(InstructionEmbryoParser(instruction_name,
                                                               program_parser),
                                       ResultTranslator())


def result_to_sh(result: ExecutionResultAndStderr) -> sh.SuccessOrHardError:
    if result.exit_code != 0:
        return sh.new_sh_hard_error(
            top_lvl_error_msg_rendering.non_zero_exit_code_msg(result.program,
                                                               result.exit_code,
                                                               result.stderr_contents)
        )
    return sh.new_sh_success()


def result_to_pfh(result: ExecutionResultAndStderr) -> pfh.PassOrFailOrHardError:
    if result.exit_code != 0:
        return pfh.new_pfh_fail(
            top_lvl_error_msg_rendering.non_zero_exit_code_msg(result.program,
                                                               result.exit_code,
                                                               result.stderr_contents)
        )
    return pfh.new_pfh_pass()
