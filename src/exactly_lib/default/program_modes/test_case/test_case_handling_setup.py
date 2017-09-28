from exactly_lib.act_phase_setups import null, command_line
from exactly_lib.act_phase_setups.util.source_code_lines_utils import all_source_code_lines
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutorConstructor, ActPhaseOsProcessExecutor, \
    ActSourceAndExecutor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep


def setup() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(ActPhaseSetup(Constructor()),
                                 IdentityPreprocessor())


class Constructor(ActSourceAndExecutorConstructor):
    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list) -> ActSourceAndExecutor:
        source_code_lines = all_source_code_lines(act_phase_instructions)
        if not source_code_lines:
            return null.Constructor().apply(os_process_executor,
                                            environment,
                                            act_phase_instructions)
        else:
            return command_line.Constructor().apply(os_process_executor,
                                                    environment,
                                                    act_phase_instructions)
