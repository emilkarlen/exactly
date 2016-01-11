from shellcheck_lib.instructions.multi_phase_instructions import env
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.before_assert import BeforeAssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh

description = env.TheDescription


class _Instruction(BeforeAssertPhaseInstruction):
    def __init__(self,
                 executor: env.Executor):
        self.executor = executor

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return env.execute_and_return_sh(self.executor, os_services)


PARSER = env.Parser(_Instruction)
