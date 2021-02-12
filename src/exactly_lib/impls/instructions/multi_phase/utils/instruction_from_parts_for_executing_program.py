import pathlib
from typing import Sequence, Optional

from exactly_lib.common.err_msg import std_err_contents
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import \
    InstructionEmbryoParserWoFileSystemLocationInfo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_part_utils import MainStepResultTranslator, \
    PartsParserFromEmbryoParser
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import InstructionPartsParser
from exactly_lib.impls.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.impls.program_execution.command_processor import CommandProcessor
from exactly_lib.impls.program_execution.processors import read_stderr_on_error
from exactly_lib.impls.program_execution.processors.read_stderr_on_error import ResultWithFiles
from exactly_lib.impls.types.program import top_lvl_error_msg_rendering
from exactly_lib.impls.types.string_source import as_stdin as str_src_as_stdin
from exactly_lib.section_document.element_parsers import misc_utils
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import pfh, sh
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.process_execution import process_output_files
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


class TheInstructionEmbryo(instruction_embryo.PhaseAgnosticInstructionEmbryo[ExecutionResultAndStderr]):
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
             settings: InstructionSettings,
             os_services: OsServices,
             ) -> ExecutionResultAndStderr:
        resolver = resolving_helper_for_instruction_env(os_services, environment)
        program = resolver.resolve_program(self._program)
        storage_dir = environment.tmp_dir__path_access.root_dir__existing

        command_processor = self._command_processor(
            os_services,
            storage_dir,
            program.stdin,
            environment.mem_buff_size,
        )

        result = command_processor.process(
            environment.proc_exe_settings,
            program.command,
        )

        return ExecutionResultAndStderr(
            result.exit_code,
            result.stderr,
            storage_dir,
            program.structure(),
        )

    @staticmethod
    def _command_processor(os_services: OsServices,
                           storage_dir: pathlib.Path,
                           stdin: Sequence[StringSource],
                           mem_buff_size: int,
                           ) -> CommandProcessor[ResultWithFiles]:
        return read_stderr_on_error.ProcessorThatStoresResultInFilesInDirAndReadsStderrOnNonZeroExitCode(
            os_services.command_executor,
            storage_dir,
            str_src_as_stdin.of_sequence(stdin, mem_buff_size),
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
                 program_parser: Parser[ProgramSdv],
                 ):
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
                source.consume(len(source.remaining_part_of_current_line))
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
