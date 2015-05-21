from shelltest import phases
from shelltest.test_case import pass_or_fail_or_hard_error_construction
from shelltest.test_case.success_or_hard_error_construction import new_success
from shelltest.test_case import success_or_validation_hard_or_error_construction
from shelltest.test_case.instructions import SuccessOrHardError
from shelltest.test_case import instructions as instrs


def as_setup(internal_instruction: instrs.InternalInstruction) -> instrs.SetupPhaseInstruction:
    return _SetupInstructionExecutor(internal_instruction)


def as_assert(internal_instruction: instrs.InternalInstruction) -> instrs.AssertPhaseInstruction:
    return _AssertInstructionExecutor(internal_instruction)


def as_cleanup(internal_instruction: instrs.InternalInstruction) -> instrs.CleanupPhaseInstruction:
    return _CleanupInstructionExecutor(internal_instruction)


class _SetupInstructionExecutor(instrs.SetupPhaseInstruction):
    def __init__(self,
                 internal_instruction: instrs.InternalInstruction,
                 ret_val: SuccessOrHardError=new_success()):
        self.__internal_instruction = internal_instruction
        self.__ret_val = ret_val

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def main(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> SuccessOrHardError:
        self.__internal_instruction.execute(phases.SETUP.name,
                                            global_environment,
                                            phase_environment)
        return self.__ret_val


class _AssertInstructionExecutor(instrs.AssertPhaseInstruction):
    def __init__(self,
                 internal_instruction: instrs.InternalInstruction,
                 ret_val: instrs.PassOrFailOrHardError=pass_or_fail_or_hard_error_construction.new_success()):
        self.__internal_instruction = internal_instruction
        self.__ret_val = ret_val

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForNamedPhase) \
            -> instrs.SuccessOrValidationErrorOrHardError:
        return success_or_validation_hard_or_error_construction.new_success()

    def main(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.PassOrFailOrHardError:
        self.__internal_instruction.execute(phases.ASSERT.name,
                                            global_environment,
                                            phase_environment)
        return self.__ret_val


class _CleanupInstructionExecutor(instrs.CleanupPhaseInstruction):
    def __init__(self,
                 internal_instruction: instrs.InternalInstruction,
                 ret_val: SuccessOrHardError=new_success()):
        self.__internal_instruction = internal_instruction
        self.__ret_val = ret_val

    def main(self,
                global_environment: instrs.GlobalEnvironmentForNamedPhase,
                phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> instrs.SuccessOrHardError:
        self.__internal_instruction.execute(phases.CLEANUP.name,
                                            global_environment,
                                            phase_environment)
        return self.__ret_val

