from exactly_lib.instructions.multi_phase_instructions import env
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            env.Parser(_Instruction),
        env.TheInstructionDocumentation(instruction_name))


class _Instruction(SetupPhaseInstruction):
    def __init__(self,
                 executor: env.Executor):
        self.executor = executor

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return env.execute_and_return_sh(self.executor, os_services)


PARSER = env.Parser(_Instruction)
