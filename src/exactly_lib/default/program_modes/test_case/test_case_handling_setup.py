from typing import Sequence

from exactly_lib.actors import null, command_line
from exactly_lib.actors.util.source_code_lines_utils import all_source_code_lines
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.actor import Actor, ActionToCheck
from exactly_lib.test_case.phases.act import ActPhaseInstruction


def setup() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(ActPhaseSetup(TheActor()),
                                 IdentityPreprocessor())


class TheActor(Actor):
    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        source_code_lines = all_source_code_lines(instructions)
        if not source_code_lines:
            return null.Parser().parse(instructions)
        else:
            return command_line.Parser().parse(instructions)
