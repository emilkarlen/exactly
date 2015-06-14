from shellcheck_lib.test_case import instructions as i
from shellcheck_lib.test_case.instructions import AssertPhaseInstruction


class InstructionWithoutValidationBase(AssertPhaseInstruction):
    def validate(self,
                 global_environment: i.GlobalEnvironmentForPostEdsPhase) -> i.SuccessOrValidationErrorOrHardError:
        return i.new_svh_success()

    def main(self, global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.PassOrFailOrHardError:
        raise NotImplementedError()

