from exactly_lib.test_case.phases.act.program_source import ScriptSourceAccumulator
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase, TestCaseInstruction, \
    GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.result.sh import SuccessOrHardError
from exactly_lib.util.line_source import LineSequence


class PhaseEnvironmentForScriptGeneration:
    """
    The phase-environment for phases that generate a script.
    """

    def __init__(self,
                 script_source_accumulator: ScriptSourceAccumulator):
        self.__script_source_accumulator = script_source_accumulator

    @property
    def append(self) -> ScriptSourceAccumulator:
        return self.__script_source_accumulator


class ActPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the ACT phase.
    """

    def source_code(self,
                    environment: GlobalEnvironmentForPreEdsStep) -> LineSequence:
        raise NotImplementedError()

    def validate_pre_eds(self,
                         environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self,
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
