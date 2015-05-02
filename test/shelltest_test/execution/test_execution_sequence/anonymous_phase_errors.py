__author__ = 'emil'

from shelltest.exec_abs_syn import instruction_result
from shelltest.exec_abs_syn.instructions import AnonymousPhaseInstruction, PhaseEnvironmentForAnonymousPhase, \
    SuccessOrHardError


class AnonymousPhaseInstructionThatReturnsHardError(AnonymousPhaseInstruction):
    def __init__(self,
                 msg: str):
        self.__msg = msg

    def execute(self,
                phase_name: str,
                global_environment,
                phase_environment: PhaseEnvironmentForAnonymousPhase) -> SuccessOrHardError:
        return instruction_result.new_hard_error(self.__msg)
