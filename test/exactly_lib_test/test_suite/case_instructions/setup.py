import unittest
from typing import List, Dict, Callable

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document.model import Instruction
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.test_suite.case_instructions.test_resources import registering_instructions
from exactly_lib_test.test_suite.case_instructions.test_resources.registering_instructions import \
    INSTRUCTION_MARKER_IN_CONTAINING_SUITE, INSTRUCTION_MARKER_IN_CASE_1, INSTRUCTION_MARKER_IN_CASE_2, PhaseConfig


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class SetupPhaseConfig(PhaseConfig):
    def phase_name(self) -> SectionName:
        return phase_names.SETUP_PHASE_NAME

    def mk_instruction_set_for_phase(self, instructions: Dict[str, SingleInstructionSetup]) -> InstructionsSetup:
        return InstructionsSetup(setup_instruction_set=instructions)

    def mk_instruction_with_main_action(self, main_action: Callable) -> Instruction:
        return setup_phase_instruction_that(main_initial_action=main_action)


class Test(registering_instructions.TestBase):
    PHASE_CONFIG = SetupPhaseConfig()

    def _phase_config(self) -> PhaseConfig:
        return self.PHASE_CONFIG

    def _expected_instruction_recording(self) -> List[str]:
        return [
            # First test case
            INSTRUCTION_MARKER_IN_CONTAINING_SUITE,
            INSTRUCTION_MARKER_IN_CASE_1,

            # Second test case
            INSTRUCTION_MARKER_IN_CONTAINING_SUITE,
            INSTRUCTION_MARKER_IN_CASE_2,
        ]

    def test_instructions_in_containing_suite_SHOULD_be_executed_first_in_each_case(self):
        self._phase_instructions_in_suite_containing_cases()

    def test_instructions_in_non_containing_suite_SHOULD_not_be_executed_in_any_case(self):
        self._phase_instructions_in_suite_not_containing_cases()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
