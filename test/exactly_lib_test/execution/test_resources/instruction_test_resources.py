from typing import Sequence, Callable, Optional

from exactly_lib.processing.parse.act_phase_source_parser import SourceCodeInstruction
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.instruction import SetupPhaseInstruction
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.result import pfh, sh, svh
from exactly_lib.test_case.test_case_status import TestCaseStatus
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.test_resources.actions import do_return, action_of

ValidatePreSdsAction = Callable[[InstructionEnvironmentForPreSdsStep], svh.SuccessOrValidationErrorOrHardError]

ValidatePostSdsAction = Callable[[InstructionEnvironmentForPostSdsStep], svh.SuccessOrValidationErrorOrHardError]

SetupMainAction = Callable[[InstructionEnvironmentForPostSdsStep,
                            InstructionSettings,
                            OsServices,
                            SetupSettingsBuilder],
                           sh.SuccessOrHardError]

SetupMainInitialAction = Callable[[InstructionEnvironmentForPostSdsStep,
                                   InstructionSettings,
                                   OsServices,
                                   SetupSettingsBuilder],
                                  None]

AssertMainAction = Callable[[InstructionEnvironmentForPostSdsStep,
                             InstructionSettings,
                             OsServices],
                            pfh.PassOrFailOrHardError]

AssertMainInitialAction = Callable[[InstructionEnvironmentForPostSdsStep,
                                    InstructionSettings,
                                    OsServices],
                                   None]

BeforeAssertMainAction = Callable[[InstructionEnvironmentForPostSdsStep,
                                   InstructionSettings,
                                   OsServices],
                                  sh.SuccessOrHardError]

BeforeAssertMainInitialAction = Callable[[InstructionEnvironmentForPostSdsStep,
                                          InstructionSettings,
                                          OsServices],
                                         None]

CleanupMainAction = Callable[[InstructionEnvironmentForPostSdsStep,
                              InstructionSettings,
                              OsServices,
                              PreviousPhase],
                             sh.SuccessOrHardError]

CleanupMainInitialAction = Callable[[InstructionEnvironmentForPostSdsStep,
                                     InstructionSettings,
                                     OsServices,
                                     PreviousPhase],
                                    None]


class ImplementationErrorTestException(Exception):
    pass


def configuration_phase_instruction_that(
        main: Callable = do_return(svh.new_svh_success()),
        main_initial_action: Optional[Callable[[ConfigurationBuilder], None]] = None,
) -> ConfigurationPhaseInstruction:
    return _ConfigurationPhaseInstructionThat(main=action_of(main_initial_action, main))


def setup_phase_instruction_that(validate_pre_sds: ValidatePreSdsAction = do_return(svh.new_svh_success()),
                                 validate_pre_sds_initial_action: Optional[Callable] = None,
                                 validate_post_setup: ValidatePostSdsAction = do_return(svh.new_svh_success()),
                                 validate_post_setup_initial_action: Optional[Callable] = None,
                                 main: SetupMainAction = do_return(sh.new_sh_success()),
                                 main_initial_action: Optional[SetupMainInitialAction] = None,
                                 symbol_usages_initial_action: Optional[Callable] = None,
                                 symbol_usages: Callable = do_return([])) -> SetupPhaseInstruction:
    return _SetupPhaseInstructionThat(action_of(validate_pre_sds_initial_action, validate_pre_sds),
                                      action_of(validate_post_setup_initial_action, validate_post_setup),
                                      action_of(main_initial_action, main),
                                      action_of(symbol_usages_initial_action, symbol_usages))


def act_phase_instruction_with_source(source_code: LineSequence =
                                      LineSequence(72, ('Dummy source code from act_phase_instruction_with_source',))
                                      ) -> ActPhaseInstruction:
    return SourceCodeInstruction(source_code)


def before_assert_phase_instruction_that(validate_pre_sds: ValidatePreSdsAction = do_return(svh.new_svh_success()),
                                         validate_pre_sds_initial_action: Optional[Callable] = None,
                                         validate_post_setup: ValidatePostSdsAction = do_return(svh.new_svh_success()),
                                         validate_post_setup_initial_action: Optional[Callable] = None,
                                         main: BeforeAssertMainAction = do_return(sh.new_sh_success()),
                                         main_initial_action: Optional[BeforeAssertMainInitialAction] = None,
                                         symbol_usages_initial_action: Optional[Callable] = None,
                                         symbol_usages: Callable = do_return([])) -> BeforeAssertPhaseInstruction:
    return _BeforeAssertPhaseInstructionThat(action_of(validate_pre_sds_initial_action, validate_pre_sds),
                                             action_of(validate_post_setup_initial_action, validate_post_setup),
                                             action_of(main_initial_action, main),
                                             action_of(symbol_usages_initial_action, symbol_usages))


def assert_phase_instruction_that(validate_pre_sds: ValidatePreSdsAction = do_return(svh.new_svh_success()),
                                  validate_pre_sds_initial_action: Optional[Callable] = None,
                                  validate_post_setup: ValidatePostSdsAction = do_return(svh.new_svh_success()),
                                  validate_post_setup_initial_action: Optional[Callable] = None,
                                  main: AssertMainAction = do_return(pfh.new_pfh_pass()),
                                  main_initial_action: Optional[AssertMainInitialAction] = None,
                                  symbol_usages_initial_action: Optional[Callable] = None,
                                  symbol_usages: Callable = do_return([])) -> AssertPhaseInstruction:
    return _AssertPhaseInstructionThat(action_of(validate_pre_sds_initial_action, validate_pre_sds),
                                       action_of(validate_post_setup_initial_action, validate_post_setup),
                                       action_of(main_initial_action, main),
                                       action_of(symbol_usages_initial_action, symbol_usages))


def cleanup_phase_instruction_that(validate_pre_sds: ValidatePreSdsAction = do_return(svh.new_svh_success()),
                                   validate_pre_sds_initial_action: Optional[Callable] = None,
                                   main: CleanupMainAction = do_return(sh.new_sh_success()),
                                   main_initial_action: Optional[CleanupMainInitialAction] = None,
                                   symbol_usages_initial_action: Optional[Callable] = None,
                                   symbol_usages: Callable = do_return([])) -> CleanupPhaseInstruction:
    return _CleanupPhaseInstructionThat(action_of(validate_pre_sds_initial_action, validate_pre_sds),
                                        action_of(main_initial_action, main),
                                        action_of(symbol_usages_initial_action, symbol_usages))


class ConfigurationPhaseInstructionThatSetsExecutionMode(ConfigurationPhaseInstruction):
    def __init__(self, value_to_set: TestCaseStatus):
        self.value_to_set = value_to_set

    def main(self, configuration_builder: ConfigurationBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        configuration_builder.set_test_case_status(self.value_to_set)
        return svh.new_svh_success()


class _ConfigurationPhaseInstructionThat(ConfigurationPhaseInstruction):
    def __init__(self,
                 main: Callable[[ConfigurationBuilder], svh.SuccessOrValidationErrorOrHardError],
                 ):
        self.do_main = main

    def main(self, configuration_builder: ConfigurationBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        return self.do_main(configuration_builder)


class _SetupPhaseInstructionThat(SetupPhaseInstruction):
    def __init__(self,
                 validate_pre_sds: ValidatePreSdsAction,
                 validate_post_setup: ValidatePostSdsAction,
                 main: SetupMainAction,
                 symbol_usages: Callable[[], Sequence[SymbolUsage]],
                 ):
        self._validate_pre_sds = validate_pre_sds
        self._validate_post_setup = validate_post_setup
        self._main = main
        self._symbol_usages = symbol_usages

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_pre_sds(environment)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return self._main(environment, settings, os_services, settings_builder)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(environment)

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbol_usages()


class _BeforeAssertPhaseInstructionThat(BeforeAssertPhaseInstruction):
    def __init__(self,
                 validate_pre_sds: ValidatePreSdsAction,
                 validate_post_setup: ValidatePostSdsAction,
                 main: BeforeAssertMainAction,
                 symbol_usages):
        self._validate_pre_sds = validate_pre_sds
        self._validate_post_setup = validate_post_setup
        self._main = main
        self._symbol_usages = symbol_usages

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbol_usages()

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_pre_sds(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(environment)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return self._main(environment, settings, os_services)


class _AssertPhaseInstructionThat(AssertPhaseInstruction):
    def __init__(self,
                 validate_pre_sds: ValidatePreSdsAction,
                 validate_post_setup: ValidatePostSdsAction,
                 main: AssertMainAction,
                 symbol_usages):
        self._validate_pre_sds = validate_pre_sds
        self._validate_post_setup = validate_post_setup
        self._main = main
        self._symbol_usages = symbol_usages

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbol_usages()

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_pre_sds(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(environment)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return self._main(environment, settings, os_services)


class _CleanupPhaseInstructionThat(CleanupPhaseInstruction):
    def __init__(self,
                 validate_pre_sds: ValidatePreSdsAction,
                 main: CleanupMainAction,
                 symbol_usages):
        self.do_validate_pre_sds = validate_pre_sds
        self.do_main = main
        self._symbol_usages = symbol_usages

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbol_usages()

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return self.do_validate_pre_sds(environment)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             previous_phase: PreviousPhase) -> sh.SuccessOrHardError:
        return self.do_main(environment, settings, os_services, previous_phase)
