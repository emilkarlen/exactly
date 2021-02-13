from typing import Sequence, Callable, Optional, Generic

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import InstructionEmbryo, T, \
    PhaseAgnosticInstructionEmbryo, SetupPhaseAwareInstructionEmbryo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib_test.impls.test_resources.validation.sdv_validators import SdvValidatorThat
from exactly_lib_test.test_resources.actions import do_return, action_of, do_nothing


def instruction_embryo_that__phase_agnostic(
        validate_pre_sds_initial_action=do_nothing,
        validate_pre_sds_return_value: Optional[TextRenderer] = None,
        validate_post_sds_initial_action=do_nothing,
        validate_post_sds_return_value: Optional[TextRenderer] = None,
        main: Callable[[InstructionEnvironmentForPostSdsStep,
                        InstructionSettings,
                        OsServices],
                       T] = do_return(
            None),
        main_initial_action: Optional[Callable[[InstructionEnvironmentForPostSdsStep,
                                                InstructionSettings,
                                                OsServices],
                                               None]] = None,
        symbol_usages_initial_action=None,
        symbol_usages=do_return([])) -> InstructionEmbryo[T]:
    return _PhaseAgnosticInstructionEmbryoThat(
        SdvValidatorThat(pre_sds_action=validate_pre_sds_initial_action,
                         pre_sds_return_value=validate_pre_sds_return_value,
                         post_setup_action=validate_post_sds_initial_action,
                         post_setup_return_value=validate_post_sds_return_value),
        action_of(main_initial_action, main),
        action_of(symbol_usages_initial_action, symbol_usages),
    )


def instruction_embryo_that__setup_phase_aware(validate_pre_sds_initial_action=do_nothing,
                                               validate_pre_sds_return_value: Optional[TextRenderer] = None,
                                               validate_post_sds_initial_action=do_nothing,
                                               validate_post_sds_return_value: Optional[TextRenderer] = None,
                                               main: Callable[[InstructionEnvironmentForPostSdsStep,
                                                               InstructionSettings,
                                                               Optional[SetupSettingsBuilder],
                                                               OsServices], T] = do_return(None),
                                               main_initial_action: Optional[
                                                   Callable[[InstructionEnvironmentForPostSdsStep,
                                                             InstructionSettings,
                                                             Optional[SetupSettingsBuilder],
                                                             OsServices], None]] = None,
                                               symbol_usages_initial_action=None,
                                               symbol_usages=do_return([])) -> InstructionEmbryo[T]:
    return _SetupPhaseAwareInstructionEmbryoThat(
        SdvValidatorThat(pre_sds_action=validate_pre_sds_initial_action,
                         pre_sds_return_value=validate_pre_sds_return_value,
                         post_setup_action=validate_post_sds_initial_action,
                         post_setup_return_value=validate_post_sds_return_value),
        action_of(main_initial_action, main),
        action_of(symbol_usages_initial_action, symbol_usages)
    )


class _PhaseAgnosticInstructionEmbryoThat(Generic[T], PhaseAgnosticInstructionEmbryo[T]):
    def __init__(self,
                 validator: SdvValidator,
                 main: Callable[[InstructionEnvironmentForPostSdsStep,
                                 InstructionSettings,
                                 OsServices],
                                T],
                 symbol_usages: Callable[[], Sequence[SymbolUsage]]):
        self._validator = validator
        self._main = main
        self._symbol_usages = symbol_usages

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbol_usages()

    @property
    def validator(self) -> SdvValidator:
        return self._validator

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ) -> T:
        return self._main(environment, settings, os_services)


class _SetupPhaseAwareInstructionEmbryoThat(Generic[T], SetupPhaseAwareInstructionEmbryo[T]):
    def __init__(self,
                 validator: SdvValidator,
                 main: Callable[[InstructionEnvironmentForPostSdsStep,
                                 InstructionSettings,
                                 Optional[SetupSettingsBuilder],
                                 OsServices], T],
                 symbol_usages: Callable[[], Sequence[SymbolUsage]]):
        self._validator = validator
        self._main = main
        self._symbol_usages = symbol_usages

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbol_usages()

    @property
    def validator(self) -> SdvValidator:
        return self._validator

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             setup_phase_settings: Optional[SetupSettingsBuilder],
             os_services: OsServices,
             ) -> T:
        return self._main(environment, settings, setup_phase_settings, os_services)
