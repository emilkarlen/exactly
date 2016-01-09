from shellcheck_lib.test_case.sections import common
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction
from shellcheck_lib.test_case.sections.act.phase_setup import PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.result import sh


class ExecutableProgramInstruction(ActPhaseInstruction):
    def __init__(self,
                 source_code: str):
        self.source_code = source_code

    def main(self, global_environment: common.GlobalEnvironmentForPostEdsPhase,
             script_generator: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        script_generator.append.raw_script_statement(self.source_code)
        return sh.new_sh_success()
