__author__ = 'emil'

from shelltest.exec_abs_syn import instruction_result
from shelltest.exec_abs_syn import instructions as instrs


class ImplementationErrorTestException(Exception):
    pass


class AnonymousPhaseInstructionThatReturnsHardError(instrs.AnonymousPhaseInstruction):
    def __init__(self,
                 msg: str):
        self.__msg = msg

    def execute(self,
                phase_name: str,
                global_environment,
                phase_environment: instrs.PhaseEnvironmentForAnonymousPhase) -> instrs.SuccessOrHardError:
        return instruction_result.new_hard_error(self.__msg)


class AnonymousPhaseInstructionWithImplementationError(instrs.AnonymousPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def execute(self,
                phase_name: str,
                global_environment,
                phase_environment: instrs.PhaseEnvironmentForAnonymousPhase) -> instrs.SuccessOrHardError:
        raise self.__exception_to_raise


class SetupPhaseInstructionThatReturnsHardError(instrs.SetupPhaseInstruction):
    def __init__(self,
                 msg: str):
        self.__msg = msg

    def execute(self,
                phase_name: str,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.SuccessOrHardError:
        return instruction_result.new_hard_error(self.__msg)

