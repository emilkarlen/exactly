from shellcheck_lib.execution import phases
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup


class HelpInstructionsSetup(tuple):
    def __new__(cls,
                instruction_set: InstructionsSetup):
        return tuple.__new__(cls, (instruction_set,))

    @property
    def plain_instruction_set(self) -> InstructionsSetup:
        return self[0]

    @property
    def phase_and_instruction_set(self) -> list:
        """
        :return: [(Phase, dict)]
        """
        return [
            (phases.ANONYMOUS, self.plain_instruction_set.config_instruction_set),
            (phases.SETUP, self.plain_instruction_set.setup_instruction_set),
            (phases.ASSERT, self.plain_instruction_set.assert_instruction_set),
            (phases.CLEANUP, self.plain_instruction_set.cleanup_instruction_set),
        ]

    @property
    def phase_2_instruction_set(self) -> dict:
        """
        :return: phase-identifier-str -> InstructionSet
        """
        return dict(map(lambda ph_is: (ph_is[0].identifier, ph_is[1]),
                        self.phase_and_instruction_set))


class ApplicationHelp(tuple):
    def __new__(cls,
                instructions_setup: HelpInstructionsSetup):
        return tuple.__new__(cls, (instructions_setup,))

    @property
    def instructions_setup(self) -> HelpInstructionsSetup:
        return self[0]
