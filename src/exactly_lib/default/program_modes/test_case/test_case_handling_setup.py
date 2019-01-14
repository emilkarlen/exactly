from typing import Sequence

from exactly_lib.act_phase_setups import null, command_line
from exactly_lib.act_phase_setups.util.source_code_lines_utils import all_source_code_lines
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.act_phase_handling import ActionToCheckExecutorParser, ActionToCheckExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction


def setup() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(ActPhaseSetup(AtcExecutorParser()),
                                 IdentityPreprocessor())


class AtcExecutorParser(ActionToCheckExecutorParser):
    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheckExecutor:
        source_code_lines = all_source_code_lines(instructions)
        if not source_code_lines:
            return null.Parser().parse(instructions)
        else:
            return command_line.Parser().parse(instructions)
