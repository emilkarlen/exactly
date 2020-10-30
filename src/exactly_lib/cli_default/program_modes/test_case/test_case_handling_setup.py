from typing import Sequence

from exactly_lib.actors import null
from exactly_lib.actors.program import actor
from exactly_lib.actors.util.source_code_lines import all_source_code_lines
from exactly_lib.definitions.entity import actors
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.actor import Actor, ActionToCheck
from exactly_lib.test_case.phases.act import ActPhaseInstruction


def setup() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(ActPhaseSetup(actors.COMMAND_LINE_ACTOR.singular_name,
                                               TheActor()),
                                 IdentityPreprocessor())


class TheActor(Actor):
    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        source_code_lines = all_source_code_lines(instructions)
        if not source_code_lines:
            return null.actor().parse(instructions)
        else:
            return actor.actor().parse(instructions)
