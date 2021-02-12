"""
Utilities for helping with integrate multi-phase instruction into different phases.
"""
from typing import Generic, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import MainStepMethodEmbryo, \
    InstructionEmbryo, InstructionEmbryoParser, T, MainMethodVisitor, RET, SetupPhaseAwareMainMethod, \
    PhaseAgnosticMainMethod
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import MainStepExecutor, \
    InstructionParts, InstructionPartsParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.result import pfh, sh


class MainStepResultTranslator(Generic[T]):
    """
    Translates a custom result to the form that is expected by instructions in different phases.

    This is a utility for constructing a `MainStepExecutor` from a generic main-step-executor.
    """

    def translate_for_non_assertion(self, main_result: T) -> sh.SuccessOrHardError:
        raise NotImplementedError()

    def translate_for_assertion(self, main_result: T) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()


class MainStepResultTranslatorForErrorMessageStringResultAsHardError(MainStepResultTranslator[str]):
    """
    Translates a str to HARD_ERROR, and None to success.
    """

    def translate_for_non_assertion(self, error_message: str) -> sh.SuccessOrHardError:
        return (
            sh.new_sh_success()
            if error_message is None
            else sh.new_sh_hard_error__str(error_message)
        )

    def translate_for_assertion(self, error_message: str) -> pfh.PassOrFailOrHardError:
        return (
            pfh.new_pfh_pass()
            if error_message is None
            else pfh.new_pfh_hard_error__str(error_message)
        )


class MainStepResultTranslatorForTextRendererAsHardError(MainStepResultTranslator[TextRenderer]):
    def translate_for_non_assertion(self, error_message: TextRenderer) -> sh.SuccessOrHardError:
        return (
            sh.new_sh_success()
            if error_message is None
            else sh.new_sh_hard_error(error_message)
        )

    def translate_for_assertion(self, error_message: TextRenderer) -> pfh.PassOrFailOrHardError:
        return (
            pfh.new_pfh_pass()
            if error_message is None
            else pfh.new_pfh_hard_error(error_message)
        )


class MainStepResultTranslatorForUnconditionalSuccess(MainStepResultTranslator):
    def translate_for_non_assertion(self, error_message) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def translate_for_assertion(self, error_message) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()


class MainStepExecutorFromMainStepExecutorEmbryo(MainStepExecutor):
    def __init__(self,
                 main_step: MainStepMethodEmbryo[T],
                 result_translator: MainStepResultTranslator[T],
                 ):
        self.result_translator = result_translator
        self.main_step = main_step

    def apply_as_non_assertion(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               settings: InstructionSettings,
                               os_services: OsServices,
                               setup_phase_settings: Optional[SetupSettingsBuilder],
                               ) -> sh.SuccessOrHardError:
        main_executor = _MainMethodExecutor(environment, settings, os_services, setup_phase_settings)
        try:
            result = self.main_step.main_method().accept(main_executor)
        except HardErrorException as ex:
            return sh.new_sh_hard_error(ex.error)

        return self.result_translator.translate_for_non_assertion(result)

    def apply_as_assertion(self,
                           environment: InstructionEnvironmentForPostSdsStep,
                           settings: InstructionSettings,
                           os_services: OsServices,
                           ) -> pfh.PassOrFailOrHardError:
        main_executor = _MainMethodExecutor(environment, settings, os_services, None)
        try:
            result = self.main_step.main_method().accept(main_executor)
        except HardErrorException as ex:
            return pfh.new_pfh_hard_error(ex.error)

        return self.result_translator.translate_for_assertion(result)


class _MainMethodExecutor(Generic[RET], MainMethodVisitor[RET, RET]):
    def __init__(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 instruction_settings: InstructionSettings,
                 os_services: OsServices,
                 setup_phase_settings: Optional[SetupSettingsBuilder],
                 ):
        self._environment = environment
        self._instruction_settings = instruction_settings
        self._os_services = os_services
        self._setup_phase_settings = setup_phase_settings

    def visit_phase_agnostic(self, main_method: PhaseAgnosticMainMethod[T]) -> RET:
        return main_method.main(self._environment, self._instruction_settings, self._os_services)

    def visit_setup_phase_aware(self, main_method: SetupPhaseAwareMainMethod[T]) -> RET:
        return main_method.main(self._environment,
                                self._instruction_settings,
                                self._setup_phase_settings,
                                self._os_services)


def instruction_parts_from_embryo(instruction: InstructionEmbryo[T],
                                  result_translator: MainStepResultTranslator[T]) -> InstructionParts:
    return InstructionParts(instruction.validator,
                            MainStepExecutorFromMainStepExecutorEmbryo(instruction, result_translator),
                            tuple(instruction.symbol_usages))


class PartsParserFromEmbryoParser(InstructionPartsParser):
    def __init__(self,
                 embryo_parser: InstructionEmbryoParser[T],
                 main_step_result_translator: MainStepResultTranslator[T],
                 ):
        self.embryo_parser = embryo_parser
        self.main_step_result_translator = main_step_result_translator

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> InstructionParts:
        instruction_embryo = self.embryo_parser.parse(fs_location_info, source)
        assert isinstance(instruction_embryo, InstructionEmbryo)
        return instruction_parts_from_embryo(instruction_embryo,
                                             self.main_step_result_translator)
