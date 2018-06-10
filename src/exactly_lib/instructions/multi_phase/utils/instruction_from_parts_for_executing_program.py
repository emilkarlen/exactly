from typing import Sequence

from exactly_lib.instructions.multi_phase.utils import instruction_embryo
from exactly_lib.instructions.multi_phase.utils.instruction_part_utils import MainStepResultTranslator, \
    PartsParserFromEmbryoParser
from exactly_lib.instructions.multi_phase.utils.instruction_parts import InstructionPartsParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths, \
    instruction_log_dir, InstructionSourceInfo
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.result import pfh, sh
from exactly_lib.util.process_execution import sub_process_execution as spe
from exactly_lib.util.process_execution.sub_process_execution import ResultAndStderr, failure_message_for_nonzero_status


class TheInstructionEmbryo(instruction_embryo.InstructionEmbryo):
    def __init__(self,
                 source_info: InstructionSourceInfo,
                 program: ProgramResolver):
        self.source_info = source_info
        self._program = program

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._program.references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._program.validator

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices) -> ResultAndStderr:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        command = self._program \
            .resolve(path_resolving_env.symbols) \
            .command \
            .value_of_any_dependency(path_resolving_env.home_and_sds)
        executable = os_services.executable_factory__detect_ex().make(command)
        executor = spe.ExecutorThatStoresResultInFilesInDir(environment.process_execution_settings)
        storage_dir = instruction_log_dir(logging_paths, self.source_info)
        return spe.execute_and_read_stderr_if_non_zero_exitcode(executable, executor, storage_dir)


class ResultAndStderrTranslator(MainStepResultTranslator):
    def translate_for_non_assertion(self, main_result) -> sh.SuccessOrHardError:
        return result_to_sh(main_result)

    def translate_for_assertion(self, main_result) -> pfh.PassOrFailOrHardError:
        return result_to_pfh(main_result)


class InstructionEmbryoParser(instruction_embryo.InstructionEmbryoParser):
    def __init__(self,
                 instruction_name: str,
                 program_parser: Parser[ProgramResolver]):
        self.instruction_name = instruction_name
        self.program_parser = program_parser

    def parse(self, source: ParseSource) -> TheInstructionEmbryo:
        source_info = InstructionSourceInfo(source.current_line_number,
                                            self.instruction_name)
        program = self.program_parser.parse(source)
        return TheInstructionEmbryo(source_info, program)


def parts_parser(instruction_name: str,
                 program_parser: Parser[ProgramResolver]
                 ) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(InstructionEmbryoParser(instruction_name,
                                                               program_parser),
                                       ResultAndStderrTranslator())


def result_to_sh(result_and_stderr: ResultAndStderr) -> sh.SuccessOrHardError:
    result = result_and_stderr.result
    if not result.is_success:
        return sh.new_sh_hard_error(result.error_message)
    if result.exit_code != 0:
        return sh.new_sh_hard_error(failure_message_for_nonzero_status(result_and_stderr))
    return sh.new_sh_success()


def result_to_pfh(result_and_stderr: ResultAndStderr) -> pfh.PassOrFailOrHardError:
    result = result_and_stderr.result
    if not result.is_success:
        return pfh.new_pfh_hard_error(failure_message_for_nonzero_status(result_and_stderr))
    if result.exit_code != 0:
        return pfh.new_pfh_fail(failure_message_for_nonzero_status(result_and_stderr))
    return pfh.new_pfh_pass()
