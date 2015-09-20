from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case import instructions as instrs


class ImplementationErrorTestException(Exception):
    pass


class AnonymousPhaseInstructionThatSetsExecutionMode(instrs.AnonymousPhaseInstruction):
    def __init__(self,
                 value_to_set: instrs.ExecutionMode):
        self.value_to_set = value_to_set

    def main(self,
             global_environment,
             phase_environment: instrs.PhaseEnvironmentForAnonymousPhase) -> sh.SuccessOrHardError:
        phase_environment.set_execution_mode(self.value_to_set)
        return sh.new_sh_success()


class AnonymousPhaseInstructionThatReturnsHardError(instrs.AnonymousPhaseInstruction):
    def __init__(self,
                 msg: str):
        self.__msg = msg

    def main(self,
             global_environment,
             phase_environment: instrs.PhaseEnvironmentForAnonymousPhase) -> sh.SuccessOrHardError:
        return sh.new_sh_hard_error(self.__msg)


class AnonymousPhaseInstructionWithImplementationError(instrs.AnonymousPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(self,
             global_environment,
             phase_environment: instrs.PhaseEnvironmentForAnonymousPhase) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise


class SetupPhaseInstructionThatReturns(instrs.SetupPhaseInstruction):
    def __init__(self,
                 from_pre_validate: svh.SuccessOrValidationErrorOrHardError,
                 from_execute: sh.SuccessOrHardError,
                 from_post_validate: svh.SuccessOrValidationErrorOrHardError):
        self.__from_pre_validate = from_pre_validate
        self.__from_execute = from_execute
        self.__from_post_validate = from_post_validate

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.__from_pre_validate

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: instrs.SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return self.__from_execute

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.__from_post_validate


class SetupPhaseInstructionWithImplementationErrorInPreValidate(instrs.SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: instrs.SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class SetupPhaseInstructionWithImplementationErrorInPostValidate(instrs.SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: instrs.SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise


class SetupPhaseInstructionWithImplementationErrorInExecute(instrs.SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: instrs.SetupSettingsBuilder) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class ActPhaseInstructionThatReturns(instrs.ActPhaseInstruction):
    def __init__(self,
                 from_validate: svh.SuccessOrValidationErrorOrHardError,
                 from_execute: sh.SuccessOrHardError):
        self.__for_validate = from_validate
        self.__for_execute = from_execute

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.__for_validate

    def main(
            self,
            global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
            phase_environment: instrs.PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        return self.__for_execute


class ActPhaseInstructionWithImplementationErrorInValidate(instrs.ActPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise

    def main(
            self,
            global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
            phase_environment: instrs.PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        return sh.new_sh_success()


class ActPhaseInstructionWithImplementationErrorInExecute(instrs.ActPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(
            self,
            global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
            phase_environment: instrs.PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise


class AssertPhaseInstructionThatReturns(instrs.AssertPhaseInstruction):
    def __init__(self,
                 from_validate: svh.SuccessOrValidationErrorOrHardError,
                 from_execute: pfh.PassOrFailOrHardError):
        self.__for_validate = from_validate
        self.__for_execute = from_execute

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.__for_validate

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> pfh.PassOrFailOrHardError:
        return self.__for_execute


class AssertPhaseInstructionWithImplementationErrorInValidate(instrs.AssertPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> pfh.PassOrFailOrHardError:
        return sh.new_sh_success()


class AssertPhaseInstructionWithImplementationErrorInExecute(instrs.AssertPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> pfh.PassOrFailOrHardError:
        raise self.__exception_to_raise


class CleanupPhaseInstructionThatReturnsHardError(instrs.CleanupPhaseInstruction):
    def __init__(self,
                 msg: str):
        self.__msg = msg

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> sh.SuccessOrHardError:
        return sh.new_sh_hard_error(self.__msg)


class CleanupPhaseInstructionWithImplementationError(instrs.CleanupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise
