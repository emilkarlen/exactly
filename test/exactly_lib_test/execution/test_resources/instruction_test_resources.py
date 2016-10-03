from exactly_lib.execution.execution_mode import ExecutionMode
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as instrs
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.util.line_source import LineSequence


def do_return(x):
    def ret_val(*args):
        return x

    return ret_val


def do_raise(ex: Exception):
    def ret_val(*args):
        raise ex

    return ret_val


class ImplementationErrorTestException(Exception):
    pass


def configuration_phase_instruction_that(main=do_return(sh.SuccessOrHardError),
                                         main_first_action=None) -> ConfigurationPhaseInstruction:
    if main_first_action:
        def complete_main(global_environment, configuration_builder):
            main_first_action(global_environment, configuration_builder)
            return main(global_environment, configuration_builder)

        return _ConfigurationPhaseInstructionThat(complete_main)
    else:
        return _ConfigurationPhaseInstructionThat(main=main)


def setup_phase_instruction_that(validate_pre_eds=do_return(svh.new_svh_success()),
                                 validate_post_setup=do_return(svh.new_svh_success()),
                                 main=do_return(sh.new_sh_success()),
                                 main_initial_action=None) -> SetupPhaseInstruction:
    if main_initial_action:
        def complete_main(environment, os_services, settings_builder):
            main_initial_action(environment, os_services, settings_builder)
            return main(environment, os_services, settings_builder)

        return _SetupPhaseInstructionThat(validate_pre_eds,
                                          validate_post_setup,
                                          complete_main)
    else:
        return _SetupPhaseInstructionThat(validate_pre_eds,
                                          validate_post_setup,
                                          main)


def act_phase_instruction_that(validate_pre_eds=do_return(svh.new_svh_success()),
                               validate_post_setup=do_return(svh.new_svh_success()),
                               main=do_return(sh.new_sh_success())) -> ActPhaseInstruction:
    return _ActPhaseInstructionThat(validate_pre_eds=validate_pre_eds,
                                    validate_post_setup=validate_post_setup,
                                    main=main)


def act_phase_instruction_with(source: LineSequence) -> ActPhaseInstruction:
    return _ActPhaseInstructionWithConstantSource(source)


def before_assert_phase_instruction_that(validate_pre_eds=do_return(svh.new_svh_success()),
                                         validate_post_setup=do_return(svh.new_svh_success()),
                                         main=do_return(sh.new_sh_success()),
                                         main_initial_action=None) -> AssertPhaseInstruction:
    if main_initial_action:
        def complete_main(environment, os_services):
            main_initial_action(environment, os_services)
            return main(environment, os_services)

        return _BeforeAssertPhaseInstructionThat(validate_pre_eds,
                                                 validate_post_setup,
                                                 complete_main)
    else:
        return _BeforeAssertPhaseInstructionThat(validate_pre_eds,
                                                 validate_post_setup,
                                                 main)


def assert_phase_instruction_that(validate_pre_eds=do_return(svh.new_svh_success()),
                                  validate_post_setup=do_return(svh.new_svh_success()),
                                  main=do_return(pfh.new_pfh_pass()),
                                  main_initial_action=None) -> AssertPhaseInstruction:
    if main_initial_action:
        def complete_main(environment, os_services):
            main_initial_action(environment, os_services)
            return main(environment, os_services)

        return _AssertPhaseInstructionThat(validate_pre_eds,
                                           validate_post_setup,
                                           complete_main)
    else:
        return _AssertPhaseInstructionThat(validate_pre_eds,
                                           validate_post_setup,
                                           main)


def cleanup_phase_instruction_that(validate_pre_eds=do_return(svh.new_svh_success()),
                                   main=do_return(sh.new_sh_success()),
                                   main_initial_action=None) -> CleanupPhaseInstruction:
    if main_initial_action:
        def complete_main(environment, previous_phase, os_services):
            main_initial_action(environment, previous_phase, os_services)
            return main(environment, previous_phase, os_services)

        return _CleanupPhaseInstructionThat(validate_pre_eds,
                                            complete_main)
    else:
        return _CleanupPhaseInstructionThat(validate_pre_eds,
                                            main)


class ConfigurationPhaseInstructionThatSetsExecutionMode(ConfigurationPhaseInstruction):
    def __init__(self,
                 value_to_set: ExecutionMode):
        self.value_to_set = value_to_set

    def main(self, global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_execution_mode(self.value_to_set)
        return sh.new_sh_success()


class _ConfigurationPhaseInstructionThat(ConfigurationPhaseInstruction):
    def __init__(self,
                 main):
        self.do_main = main

    def main(self, global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        return self.do_main(global_environment, configuration_builder)


class _SetupPhaseInstructionThat(SetupPhaseInstruction):
    def __init__(self,
                 validate_pre_eds,
                 validate_post_setup,
                 main):
        self._validate_pre_eds = validate_pre_eds
        self._validate_post_setup = validate_post_setup
        self._main = main

    def validate_pre_eds(self,
                         environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_pre_eds(environment)

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return self._main(environment, os_services, settings_builder)

    def validate_post_setup(self,
                            environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(environment)


class _ActPhaseInstructionThat(ActPhaseInstruction):
    def __init__(self,
                 validate_pre_eds,
                 validate_post_setup,
                 main):
        self._validate_pre_eds = validate_pre_eds
        self._validate_post_setup = validate_post_setup
        self._main = main

    def validate_pre_eds(self,
                         environment: instrs.GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_pre_eds(environment)

    def validate_post_setup(self,
                            global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(global_environment)

    def main(
            self,
            global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        return self._main(global_environment, phase_environment)


class _ActPhaseInstructionWithConstantSource(ActPhaseInstruction):
    def __init__(self,
                 source: LineSequence):
        self.source = source

    def source_code(self, environment: GlobalEnvironmentForPreEdsStep) -> LineSequence:
        return self.source

    def validate_pre_eds(self,
                         environment: instrs.GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        raise RuntimeError('deprecated - should not be used')

    def validate_post_setup(self,
                            global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise RuntimeError('deprecated - should not be used')

    def main(
            self,
            global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        raise RuntimeError('deprecated - should not be used')


class _BeforeAssertPhaseInstructionThat(BeforeAssertPhaseInstruction):
    def __init__(self,
                 validate_pre_eds,
                 validate_post_setup,
                 main):
        self._validate_pre_eds = validate_pre_eds
        self._validate_post_setup = validate_post_setup
        self._main = main

    def validate_pre_eds(self,
                         environment: instrs.GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_pre_eds(environment)

    def validate_post_setup(self,
                            environment: instrs.GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(environment)

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return self._main(environment, os_services)


class _AssertPhaseInstructionThat(AssertPhaseInstruction):
    def __init__(self,
                 validate_pre_eds,
                 validate_post_setup,
                 main):
        self._validate_pre_eds = validate_pre_eds
        self._validate_post_setup = validate_post_setup
        self._main = main

    def validate_pre_eds(self,
                         environment: instrs.GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_pre_eds(environment)

    def validate_post_setup(self,
                            environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(environment)

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return self._main(environment, os_services)


class _CleanupPhaseInstructionThat(CleanupPhaseInstruction):
    def __init__(self,
                 validate_pre_eds,
                 main):
        self.do_validate_pre_eds = validate_pre_eds
        self.do_main = main

    def validate_pre_eds(self,
                         environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.do_validate_pre_eds(environment)

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return self.do_main(environment, previous_phase, os_services)
