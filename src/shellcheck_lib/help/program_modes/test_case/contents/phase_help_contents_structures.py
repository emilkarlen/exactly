from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseHelp, \
    TestCasePhaseInstructionSet
from shellcheck_lib.help.utils.description import Description


class TestCasePhaseHelpForPhaseWithInstructions(TestCasePhaseHelp):
    def __init__(self,
                 name: str,
                 description: Description,
                 instruction_set: TestCasePhaseInstructionSet):
        """
        :param instruction_set: None if this phase does not have instructions.
        """
        super().__init__(name)
        self._description = description
        self._instruction_set = instruction_set

    @property
    def description(self) -> Description:
        return self._description

    @property
    def is_phase_with_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> TestCasePhaseInstructionSet:
        return self._instruction_set


class TestCasePhaseHelpForPhaseWithoutInstructions(TestCasePhaseHelp):
    def __init__(self,
                 name: str,
                 description: Description):
        super().__init__(name)
        self._description = description

    @property
    def description(self) -> Description:
        return self._description

    @property
    def is_phase_with_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> TestCasePhaseInstructionSet:
        return None
