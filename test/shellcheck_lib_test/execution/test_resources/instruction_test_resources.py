from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common as instrs
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction, ExecutionMode, \
    ConfigurationBuilder
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


def do_return(x):
    def ret_val():
        return x

    return ret_val


def do_raise(ex: Exception):
    def ret_val():
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


def anonymous_phase_instruction_that(do_main=do_return(sh.SuccessOrHardError)) -> AnonymousPhaseInstruction:
    return AnonymousPhaseInstructionThat(do_main=do_main)


class AnonymousPhaseInstructionThat(AnonymousPhaseInstruction):
    def __init__(self,
                 do_main=do_return(sh.SuccessOrHardError)):
        self.do_main = do_main

    def main(self, global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        return self.do_main()


def setup_phase_instruction_that(pre_validate=do_return(svh.new_svh_success()),
                                 main=do_return(sh.new_sh_success()),
                                 post_validate=do_return(svh.new_svh_success())) -> SetupPhaseInstruction:
    return SetupPhaseInstructionThat(pre_validate,
                                     main,
                                     post_validate)


class SetupPhaseInstructionThat(SetupPhaseInstruction):
    def __init__(self,
                 pre_validate,
                 main,
                 post_validate):
        self._pre_validate = pre_validate
        self._main = main
        self._post_validate = post_validate

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._pre_validate()

    def main(self,
             os_services: OsServices,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return self._main()

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self._post_validate()


def act_phase_instruction_that(do_validate=do_return(svh.new_svh_success()),
                               do_main=do_return(sh.new_sh_success())) -> ActPhaseInstruction:
    return ActPhaseInstructionThat(do_validate=do_validate,
                                   do_main=do_main)


class ActPhaseInstructionThat(ActPhaseInstruction):
    def __init__(self,
                 do_validate=do_return(svh.new_svh_success()),
                 do_main=do_return(sh.new_sh_success())):
        self.do_validate = do_validate
        self.do_main = do_main

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.do_validate()

    def main(
            self,
            global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        return self.do_main()


def assert_phase_instruction_that(validate=do_return(svh.new_svh_success()),
                                  main=do_return(pfh.new_pfh_pass())) -> AssertPhaseInstruction:
    return AssertPhaseInstructionThat(do_validate=validate,
                                      do_main=main)


def assert_phase_instruction_that_returns(
        from_validate: svh.SuccessOrValidationErrorOrHardError = svh.new_svh_success(),
        from_main: pfh.PassOrFailOrHardError = pfh.new_pfh_pass()) -> AssertPhaseInstruction:
    return AssertPhaseInstructionThat(do_validate=do_return(from_validate),
                                      do_main=do_return(from_main))


class AssertPhaseInstructionThat(AssertPhaseInstruction):
    def __init__(self,
                 do_validate_pre_eds=do_return(svh.new_svh_success()),
                 do_validate=do_return(svh.new_svh_success()),
                 do_main=do_return(pfh.new_pfh_pass())):
        self.do_validate_pre_eds = do_validate_pre_eds
        self.do_validate = do_validate
        self.do_main = do_main

    def validate_pre_eds(self,
                         environment: instrs.GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self.do_validate_pre_eds()

    def validate(self,
                 environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.do_validate()

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return self.do_main()


def cleanup_phase_instruction_that(do_validate_pre_eds=do_return(svh.SuccessOrValidationErrorOrHardError),
                                   do_main=do_return(sh.SuccessOrHardError)) -> CleanupPhaseInstruction:
    return CleanupPhaseInstructionThat(do_validate_pre_eds=do_validate_pre_eds,
                                       do_main=do_main)


class CleanupPhaseInstructionThat(CleanupPhaseInstruction):
    def __init__(self,
                 do_validate_pre_eds=do_return(svh.SuccessOrValidationErrorOrHardError),
                 do_main=do_return(sh.SuccessOrHardError)):
        self.do_validate_pre_eds = do_validate_pre_eds
        self.do_main = do_main

    def validate_pre_eds(self,
                         environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.do_validate_pre_eds()

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return self.do_main()
