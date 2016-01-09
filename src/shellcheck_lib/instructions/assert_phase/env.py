from shellcheck_lib.instructions.multi_phase_instructions import env
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh

description = env.TheDescription


class _Instruction(AssertPhaseInstruction):
    def __init__(self,
                 executor: env.Executor):
        self.executor = executor

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        self.executor.execute(os_services)
        return pfh.new_pfh_pass()


PARSER = env.Parser(_Instruction)
