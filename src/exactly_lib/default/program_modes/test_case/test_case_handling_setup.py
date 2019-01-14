from typing import Sequence

from exactly_lib.act_phase_setups import null, command_line
from exactly_lib.act_phase_setups.util.source_code_lines_utils import all_source_code_lines
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutorConstructor, ActSourceAndExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction


def setup() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(ActPhaseSetup(Constructor()),
                                 IdentityPreprocessor())


class Constructor(ActSourceAndExecutorConstructor):
    def parse(self,
              act_phase_instructions: Sequence[ActPhaseInstruction]) -> ActSourceAndExecutor:
        source_code_lines = all_source_code_lines(act_phase_instructions)
        if not source_code_lines:
            return null.Constructor().parse(act_phase_instructions)
        else:
            return command_line.Constructor().parse(act_phase_instructions)
