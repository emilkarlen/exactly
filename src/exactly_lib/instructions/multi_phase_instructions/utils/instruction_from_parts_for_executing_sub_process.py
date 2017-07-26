from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import MainStepResultTranslator, \
    PartsParserFromEmbryoParser
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import InstructionPartsParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case_utils import sub_process_execution as spe
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.sub_process_execution import ResultAndStderr


class SubProcessExecutionSetup:
    def __init__(self,
                 cmd_and_args_resolver: spe.CmdAndArgsResolver,
                 is_shell: bool):
        self.cmd_and_args_resolver = cmd_and_args_resolver
        self.is_shell = is_shell


class ValidationAndSubProcessExecutionSetup(SubProcessExecutionSetup):
    def __init__(self,
                 validator: PreOrPostSdsValidator,
                 cmd_and_args_resolver: spe.CmdAndArgsResolver,
                 is_shell: bool):
        super().__init__(cmd_and_args_resolver, is_shell)
        self.validator = validator


class TheInstructionEmbryo(instruction_embryo.InstructionEmbryo):
    def __init__(self,
                 source_info: spe.InstructionSourceInfo,
                 sub_process_execution_setup: ValidationAndSubProcessExecutionSetup):
        self.source_info = source_info
        self.setup = sub_process_execution_setup

    @property
    def symbol_usages(self) -> list:
        return self.setup.cmd_and_args_resolver.symbol_usages

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self.setup.validator

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices) -> ResultAndStderr:
        # The structures and implementation here does not feel good, - a candidate for refactoring!
        # E.g. ExecuteInfo may be unnecessary.
        # This implementation was copied from earlier code that was existed in many places - so that
        # it had the purpose of being reusable in many places!
        # After the refactoring that introduced this class, this implementation should perhaps be refactored.
        # But no time for this now!
        execute_info = spe.ExecuteInfo(
            self.source_info,
            self.setup.cmd_and_args_resolver.resolve(environment.path_resolving_environment_pre_or_post_sds))
        executor = spe.ExecutorThatStoresResultInFilesInDir(
            self.setup.is_shell,
            environment.process_execution_settings)
        return spe.execute_and_read_stderr_if_non_zero_exitcode(execute_info, executor, logging_paths)


class ResultAndStderrTranslator(MainStepResultTranslator):
    def translate_for_non_assertion(self, main_result) -> sh.SuccessOrHardError:
        return spe.result_to_sh(main_result)

    def translate_for_assertion(self, main_result) -> pfh.PassOrFailOrHardError:
        return spe.result_to_pfh(main_result)


class ValidationAndSubProcessExecutionSetupParser:
    def parse(self, source: ParseSource) -> ValidationAndSubProcessExecutionSetup:
        raise NotImplementedError()


class InstructionEmbryoParser(instruction_embryo.InstructionEmbryoParser):
    def __init__(self,
                 instruction_name: str,
                 setup_parser: ValidationAndSubProcessExecutionSetupParser):
        self.instruction_name = instruction_name
        self.setup_parser = setup_parser

    def parse(self, source: ParseSource) -> TheInstructionEmbryo:
        source_info = spe.InstructionSourceInfo(source.current_line_number,
                                                self.instruction_name)
        setup = self.setup_parser.parse(source)
        return TheInstructionEmbryo(source_info, setup)


def parts_parser(instruction_name: str,
                 setup_parser: ValidationAndSubProcessExecutionSetupParser
                 ) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(InstructionEmbryoParser(instruction_name,
                                                               setup_parser),
                                       ResultAndStderrTranslator())
