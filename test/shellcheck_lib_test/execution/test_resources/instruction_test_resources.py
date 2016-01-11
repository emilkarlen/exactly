from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common as instrs
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction, ExecutionMode, \
    ConfigurationBuilder
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.before_assert import BeforeAssertPhaseInstruction
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


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


class AnonymousPhaseInstructionThatSetsExecutionMode(AnonymousPhaseInstruction):
    def __init__(self,
                 value_to_set: ExecutionMode):
        self.value_to_set = value_to_set

    def main(self, global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_execution_mode(self.value_to_set)
        return sh.new_sh_success()


def anonymous_phase_instruction_that(main=do_return(sh.SuccessOrHardError)) -> AnonymousPhaseInstruction:
    return AnonymousPhaseInstructionThat(main=main)


class AnonymousPhaseInstructionThat(AnonymousPhaseInstruction):
    def __init__(self,
                 main):
        self.do_main = main

    def main(self, global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        return self.do_main(global_environment, configuration_builder)


def setup_phase_instruction_that(validate_pre_eds=do_return(svh.new_svh_success()),
                                 validate_post_setup=do_return(svh.new_svh_success()),
                                 main=do_return(sh.new_sh_success()), ) -> SetupPhaseInstruction:
    return SetupPhaseInstructionThat(validate_pre_eds,
                                     validate_post_setup,
                                     main)


class SetupPhaseInstructionThat(SetupPhaseInstruction):
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
             os_services: OsServices,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return self._main(environment, os_services, settings_builder)

    def validate_post_setup(self,
                            environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._validate_post_setup(environment)


def act_phase_instruction_that(validate_pre_eds=do_return(svh.new_svh_success()),
                               validate_post_setup=do_return(svh.new_svh_success()),
                               main=do_return(sh.new_sh_success())) -> ActPhaseInstruction:
    return ActPhaseInstructionThat(validate_pre_eds=validate_pre_eds,
                                   validate_post_setup=validate_post_setup,
                                   main=main)


class ActPhaseInstructionThat(ActPhaseInstruction):
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
        return self._main((global_environment, phase_environment))


def before_assert_phase_instruction_that(validate_pre_eds=do_return(svh.new_svh_success()),
                                         validate_post_setup=do_return(svh.new_svh_success()),
                                         main=do_return(sh.new_sh_success())) -> AssertPhaseInstruction:
    return BeforeAssertPhaseInstructionThat(validate_pre_eds,
                                            validate_post_setup,
                                            main)


class BeforeAssertPhaseInstructionThat(BeforeAssertPhaseInstruction):
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
             os_services: OsServices,
             environment: instrs.GlobalEnvironmentForPostEdsPhase) -> sh.SuccessOrHardError:
        return self._main(environment)


def assert_phase_instruction_that(validate_pre_eds=do_return(svh.new_svh_success()),
                                  validate_post_setup=do_return(svh.new_svh_success()),
                                  main=do_return(pfh.new_pfh_pass())) -> AssertPhaseInstruction:
    return AssertPhaseInstructionThat(validate_pre_eds,
                                      validate_post_setup,
                                      main)


class AssertPhaseInstructionThat(AssertPhaseInstruction):
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
        return self._main(environment)


def cleanup_phase_instruction_that(validate_pre_eds=do_return(svh.new_svh_success()),
                                   main=do_return(sh.new_sh_success())) -> CleanupPhaseInstruction:
    return CleanupPhaseInstructionThat(validate_pre_eds,
                                       main)


class CleanupPhaseInstructionThat(CleanupPhaseInstruction):
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
             os_services: OsServices) -> sh.SuccessOrHardError:
        return self.do_main(environment)
