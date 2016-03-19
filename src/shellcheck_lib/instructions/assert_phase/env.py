from shellcheck_lib.instructions.multi_phase_instructions import env
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.phases.result import pfh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            PARSER,
        env.TheInstructionReference(instruction_name))


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
