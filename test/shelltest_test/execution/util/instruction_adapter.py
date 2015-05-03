from shelltest.exec_abs_syn.instruction_result import new_success
from shelltest.exec_abs_syn.instructions import SuccessOrHardError

__author__ = 'karlen'

from shelltest.exec_abs_syn import instructions


def as_setup(internal_instruction: instructions.InternalInstruction) -> instructions.SetupPhaseInstruction:
    return _SetupInstructionExecutor(internal_instruction)


def as_assert(internal_instruction: instructions.InternalInstruction) -> instructions.AssertPhaseInstruction:
    return _AssertInstructionExecutor(internal_instruction)


def as_cleanup(internal_instruction: instructions.InternalInstruction) -> instructions.CleanupPhaseInstruction:
    return _CleanupInstructionExecutor(internal_instruction)


class _SetupInstructionExecutor(instructions.SetupPhaseInstruction):
    def __init__(self,
                 internal_instruction: instructions.InternalInstruction,
                 ret_val: SuccessOrHardError=new_success()):
        self.__internal_instruction = internal_instruction
        self.__ret_val = ret_val

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands) -> SuccessOrHardError:
        self.__internal_instruction.execute(phase_name,
                                            global_environment,
                                            phase_environment)
        return self.__ret_val


class _AssertInstructionExecutor(instructions.AssertPhaseInstruction):
    def __init__(self,
                 internal_instruction: instructions.InternalInstruction):
        self.__internal_instruction = internal_instruction

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        self.__internal_instruction.execute(phase_name,
                                            global_environment,
                                            phase_environment)


class _CleanupInstructionExecutor(instructions.CleanupPhaseInstruction):
    def __init__(self,
                 internal_instruction: instructions.InternalInstruction):
        self.__internal_instruction = internal_instruction

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        self.__internal_instruction.execute(phase_name,
                                            global_environment,
                                            phase_environment)

