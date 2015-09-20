from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction import common as instrs
from shellcheck_lib.test_case.instruction.sections.anonymous import AnonymousPhaseInstruction, ExecutionMode, \
    PhaseEnvironmentForAnonymousPhase
from shellcheck_lib.test_case.instruction.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib.test_case.instruction.sections.act import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.instruction.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.instruction.sections.cleanup import CleanupPhaseInstruction


class ImplementationErrorTestException(Exception):
    pass


class AnonymousPhaseInstructionThatSetsExecutionMode(AnonymousPhaseInstruction):
    def __init__(self,
                 value_to_set: ExecutionMode):
        self.value_to_set = value_to_set

    def main(self,
             global_environment,
             phase_environment: PhaseEnvironmentForAnonymousPhase) -> sh.SuccessOrHardError:
        phase_environment.set_execution_mode(self.value_to_set)
        return sh.new_sh_success()


class AnonymousPhaseInstructionThatReturnsHardError(AnonymousPhaseInstruction):
    def __init__(self,
                 msg: str):
        self.__msg = msg

    def main(self,
             global_environment,
             phase_environment: PhaseEnvironmentForAnonymousPhase) -> sh.SuccessOrHardError:
        return sh.new_sh_hard_error(self.__msg)


class AnonymousPhaseInstructionWithImplementationError(AnonymousPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(self,
             global_environment,
             phase_environment: PhaseEnvironmentForAnonymousPhase) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise


class SetupPhaseInstructionThatReturns(SetupPhaseInstruction):
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
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return self.__from_execute

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.__from_post_validate


class SetupPhaseInstructionWithImplementationErrorInPreValidate(SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class SetupPhaseInstructionWithImplementationErrorInPostValidate(SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise


class SetupPhaseInstructionWithImplementationErrorInExecute(SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class ActPhaseInstructionThatReturns(ActPhaseInstruction):
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
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        return self.__for_execute


class ActPhaseInstructionWithImplementationErrorInValidate(ActPhaseInstruction):
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
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        return sh.new_sh_success()


class ActPhaseInstructionWithImplementationErrorInExecute(ActPhaseInstruction):
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
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise


class AssertPhaseInstructionThatReturns(AssertPhaseInstruction):
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


class AssertPhaseInstructionWithImplementationErrorInValidate(AssertPhaseInstruction):
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


class AssertPhaseInstructionWithImplementationErrorInExecute(AssertPhaseInstruction):
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


class CleanupPhaseInstructionThatReturnsHardError(CleanupPhaseInstruction):
    def __init__(self,
                 msg: str):
        self.__msg = msg

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> sh.SuccessOrHardError:
        return sh.new_sh_hard_error(self.__msg)


class CleanupPhaseInstructionWithImplementationError(CleanupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise
