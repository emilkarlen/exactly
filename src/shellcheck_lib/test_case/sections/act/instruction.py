from shellcheck_lib.test_case.sections.act.phase_setup import PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, TestCaseInstruction
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.result.sh import SuccessOrHardError


class ActPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the ACT phase.
    """

    def validate(self,
                 global_environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             global_environment: GlobalEnvironmentForPostEdsPhase,
             phase_environment: PhaseEnvironmentForScriptGeneration) -> SuccessOrHardError:
        """
        Builds the script, and sets some execution premises (e.g. stdin),
        by updating the phase environment.

        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()
