from shellcheck_lib.execution import phases
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case import instructions as instrs


def as_setup(internal_instruction: instrs.InternalInstruction) -> instrs.SetupPhaseInstruction:
    return _SetupInstructionExecutor(internal_instruction)


def as_assert(internal_instruction: instrs.InternalInstruction) -> instrs.AssertPhaseInstruction:
    return _AssertInstructionExecutor(internal_instruction)


def as_cleanup(internal_instruction: instrs.InternalInstruction) -> instrs.CleanupPhaseInstruction:
    return _CleanupInstructionExecutor(internal_instruction)


class _SetupInstructionExecutor(instrs.SetupPhaseInstruction):
    def __init__(self,
                 internal_instruction: instrs.InternalInstruction,
                 ret_val: sh.SuccessOrHardError=sh.new_sh_success()):
        self.__internal_instruction = internal_instruction
        self.__ret_val = ret_val

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: instrs.SetupSettingsBuilder) -> sh.SuccessOrHardError:
        self.__internal_instruction.execute(phases.SETUP.name,
                                            global_environment,
                                            instrs.PhaseEnvironmentForInternalCommands())
        return self.__ret_val

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class _AssertInstructionExecutor(instrs.AssertPhaseInstruction):
    def __init__(self,
                 internal_instruction: instrs.InternalInstruction,
                 ret_val: pfh.PassOrFailOrHardError=pfh.new_pfh_pass()):
        self.__internal_instruction = internal_instruction
        self.__ret_val = ret_val

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> pfh.PassOrFailOrHardError:
        self.__internal_instruction.execute(phases.ASSERT.name,
                                            global_environment,
                                            phase_environment)
        return self.__ret_val


class _CleanupInstructionExecutor(instrs.CleanupPhaseInstruction):
    def __init__(self,
                 internal_instruction: instrs.InternalInstruction,
                 ret_val: sh.SuccessOrHardError=sh.new_sh_success()):
        self.__internal_instruction = internal_instruction
        self.__ret_val = ret_val

    def main(self,
             global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
             phase_environment: instrs.PhaseEnvironmentForInternalCommands) -> sh.SuccessOrHardError:
        self.__internal_instruction.execute(phases.CLEANUP.name,
                                            global_environment,
                                            phase_environment)
        return self.__ret_val
