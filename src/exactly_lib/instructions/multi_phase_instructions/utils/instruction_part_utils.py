"""
Utilities for helping with integrate multi-phase instruction into different phases.
"""
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_embryo import MainStepExecutorEmbryo, \
    InstructionEmbryo, InstructionEmbryoParser
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import MainStepExecutor, \
    InstructionParts, InstructionPartsParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case.phases.result import sh, pfh


class MainStepResultTranslator:
    """
    Translates a custom result to the form that is expected by instructions in different phases.

    This is a utility for constructing a `MainStepExecutor` from a generic main-step-executor.
    """

    def translate_for_non_assertion(self, main_result) -> sh.SuccessOrHardError:
        raise NotImplementedError()

    def translate_for_assertion(self, main_result) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()


class MainStepResultTranslatorForErrorMessageStringResultAsHardError(MainStepResultTranslator):
    """
    Translates a str to HARD_ERROR, and None to success.
    """

    def translate_for_non_assertion(self, error_message) -> sh.SuccessOrHardError:
        return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)

    def translate_for_assertion(self, error_message) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass() if error_message is None else pfh.new_pfh_hard_error(error_message)


class MainStepResultTranslatorForUnconditionalSuccess(MainStepResultTranslator):
    def translate_for_non_assertion(self, error_message) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def translate_for_assertion(self, error_message) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()


class MainStepExecutorFromMainStepExecutorEmbryo(MainStepExecutor):
    def __init__(self,
                 main_step_embryo: MainStepExecutorEmbryo,
                 result_translator: MainStepResultTranslator):
        self.result_translator = result_translator
        self.main_step_embryo = main_step_embryo

    def apply_as_non_assertion(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               logging_paths: PhaseLoggingPaths,
                               os_services: OsServices) -> sh.SuccessOrHardError:
        result = self.main_step_embryo.main(environment, logging_paths, os_services)
        return self.result_translator.translate_for_non_assertion(result)

    def apply_as_assertion(self,
                           environment: InstructionEnvironmentForPostSdsStep,
                           logging_paths: PhaseLoggingPaths,
                           os_services: OsServices) -> pfh.PassOrFailOrHardError:
        result = self.main_step_embryo.main(environment, logging_paths, os_services)
        return self.result_translator.translate_for_assertion(result)


def instruction_parts_from_embryo(instruction: InstructionEmbryo,
                                  result_translator: MainStepResultTranslator) -> InstructionParts:
    return InstructionParts(instruction.validator,
                            MainStepExecutorFromMainStepExecutorEmbryo(instruction, result_translator),
                            tuple(instruction.symbol_usages))


class PartsParserFromEmbryoParser(InstructionPartsParser):
    def __init__(self,
                 embryo_parser: InstructionEmbryoParser,
                 main_step_result_translator: MainStepResultTranslator):
        self.embryo_parser = embryo_parser
        self.main_step_result_translator = main_step_result_translator

    def parse(self, source: ParseSource) -> InstructionParts:
        instruction_embryo = self.embryo_parser.parse(source)
        assert isinstance(instruction_embryo, InstructionEmbryo)
        return instruction_parts_from_embryo(instruction_embryo,
                                             self.main_step_result_translator)
