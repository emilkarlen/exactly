from shelltest.execution.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from shelltest import phases
from shelltest.exec_abs_syn import instructions as instr


def _from_success_or_hard_error(res: instr.SuccessOrHardError) -> PartialInstructionControlledFailureInfo:
    return None \
        if res.is_success \
        else PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.HARD_ERROR,
                                                     res.failure_message)


class AnonymousPhaseInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 phase_environment: instr.PhaseEnvironmentForAnonymousPhase):
        self.__phase_environment = phase_environment
        self.__global_environment = ()

    def apply(self, instruction: instr.AnonymousPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.execute(phases.ANONYMOUS.name,
                                self.__global_environment,
                                self.__phase_environment))


class SetupPhaseInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForNamedPhase,
                 phase_environment: instr.PhaseEnvironmentForInternalCommands):
        self.__global_environment = global_environment
        self.__phase_environment = phase_environment

    def apply(self, instruction: instr.SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.execute(phases.SETUP.name,
                                self.__global_environment,
                                self.__phase_environment))


class ActScriptGenerationExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForNamedPhase,
                 phase_environment: instr.PhaseEnvironmentForScriptGeneration):
        self.__global_environment = global_environment
        self.__phase_environment = phase_environment

    def apply(self, instruction: instr.ActPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.update_phase_environment(phases.ACT.name,
                                                 self.__global_environment,
                                                 self.__phase_environment))
