from shelltest.test_case import success_or_hard_error_construction, success_or_validation_hard_or_error_construction
from shelltest.test_case import instructions as instrs


class ImplementationErrorTestException(Exception):
    pass


class AnonymousPhaseInstructionThatSetsExecutionMode(instrs.AnonymousPhaseInstruction):
    def __init__(self,
                 value_to_set: instrs.ExecutionMode):
        self.value_to_set = value_to_set

    def main(self,
                global_environment,
                phase_environment: instrs.PhaseEnvironmentForAnonymousPhase) -> instrs.SuccessOrHardError:
        phase_environment.set_execution_mode(self.value_to_set)
        return success_or_hard_error_construction.new_success()


class AnonymousPhaseInstructionThatReturnsHardError(instrs.AnonymousPhaseInstruction):
    def __init__(self,
                 msg: str):
        self.__msg = msg

    def main(self,
                global_environment,
                phase_environment: instrs.PhaseEnvironmentForAnonymousPhase) -> instrs.SuccessOrHardError:
        return success_or_hard_error_construction.new_hard_error(self.__msg)


class AnonymousPhaseInstructionWithImplementationError(instrs.AnonymousPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(self,
                global_environment,
                phase_environment: instrs.PhaseEnvironmentForAnonymousPhase) -> instrs.SuccessOrHardError:
        raise self.__exception_to_raise


class SetupPhaseInstructionThatReturns(instrs.SetupPhaseInstruction):
    def __init__(self,
                 from_validate: instrs.SuccessOrValidationErrorOrHardError,
                 from_execute: instrs.SuccessOrHardError):
        self.__from_validate = from_validate
        self.__from_execute = from_execute

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        return self.__from_validate

    def main(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.SuccessOrHardError:
        return self.__from_execute


class SetupPhaseInstructionWithImplementationErrorInValidate(instrs.SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise

    def main(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.SuccessOrHardError:
        return success_or_hard_error_construction.new_success()


class SetupPhaseInstructionWithImplementationErrorInExecute(instrs.SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def main(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.SuccessOrHardError:
        raise self.__exception_to_raise


class ActPhaseInstructionThatReturns(instrs.ActPhaseInstruction):
    def __init__(self,
                 from_validate: instrs.SuccessOrValidationErrorOrHardError,
                 from_execute: instrs.SuccessOrHardError):
        self.__for_validate = from_validate
        self.__for_execute = from_execute

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForNamedPhase) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        return self.__for_validate

    def update_phase_environment(
            self,
            global_environment: instrs.GlobalEnvironmentForNamedPhase,
            phase_environment: instrs.PhaseEnvironmentForScriptGeneration) -> instrs.SuccessOrHardError:
        return self.__for_execute


class ActPhaseInstructionWithImplementationErrorInValidate(instrs.ActPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForNamedPhase) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise

    def update_phase_environment(
            self,
            global_environment: instrs.GlobalEnvironmentForNamedPhase,
            phase_environment: instrs.PhaseEnvironmentForScriptGeneration) -> instrs.SuccessOrHardError:
        return success_or_hard_error_construction.new_success()


class ActPhaseInstructionWithImplementationErrorInExecute(instrs.ActPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForNamedPhase) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def update_phase_environment(
            self,
            global_environment: instrs.GlobalEnvironmentForNamedPhase,
            phase_environment: instrs.PhaseEnvironmentForScriptGeneration) -> instrs.SuccessOrHardError:
        raise self.__exception_to_raise


class AssertPhaseInstructionThatReturns(instrs.AssertPhaseInstruction):
    def __init__(self,
                 from_validate: instrs.SuccessOrValidationErrorOrHardError,
                 from_execute: instrs.PassOrFailOrHardError):
        self.__for_validate = from_validate
        self.__for_execute = from_execute

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForNamedPhase) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        return self.__for_validate

    def execute(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.PassOrFailOrHardError:
        return self.__for_execute


class AssertPhaseInstructionWithImplementationErrorInValidate(instrs.AssertPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForNamedPhase) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise

    def execute(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.PassOrFailOrHardError:
        return success_or_hard_error_construction.new_success()


class AssertPhaseInstructionWithImplementationErrorInExecute(instrs.AssertPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForNamedPhase) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def execute(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.PassOrFailOrHardError:
        raise self.__exception_to_raise


class CleanupPhaseInstructionThatReturnsHardError(instrs.CleanupPhaseInstruction):
    def __init__(self,
                 msg: str):
        self.__msg = msg

    def execute(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.SuccessOrHardError:
        return success_or_hard_error_construction.new_hard_error(self.__msg)


class CleanupPhaseInstructionWithImplementationError(instrs.CleanupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def execute(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.SuccessOrHardError:
        raise self.__exception_to_raise
