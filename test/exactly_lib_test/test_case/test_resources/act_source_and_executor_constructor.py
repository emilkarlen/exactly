from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutorConstructor, ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep


class ActSourceAndExecutorConstructorThatRaisesException(ActSourceAndExecutorConstructor):
    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list):
        raise ValueError('the method should never be called')
