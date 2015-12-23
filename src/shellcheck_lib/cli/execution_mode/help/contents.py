class TestCasePhaseInstructionSet(tuple):
    def __new__(cls,
                instruction_descriptions: iter):
        """
        :type instruction_descriptions: [Description]
        """
        return tuple.__new__(cls, (list(instruction_descriptions),))

    @property
    def instruction_descriptions(self) -> list:
        """
        :type: [Description]
        """
        return self[0]

    @property
    def name_2_description(self) -> dict:
        return dict(map(lambda description: (description.instruction_name(), description),
                        self.instruction_descriptions))


class TestCasePhaseHelp(tuple):
    def __new__(cls,
                name: str,
                instruction_set: TestCasePhaseInstructionSet):
        """

        :param name:
        :param instruction_set: None if this phase does not have instructions.
        """
        return tuple.__new__(cls, (name, instruction_set))

    @property
    def name(self) -> str:
        return self[0]

    @property
    def is_phase_with_instructions(self) -> bool:
        return self.instruction_set is not None

    @property
    def instruction_set(self) -> TestCasePhaseInstructionSet:
        """
        :return: None if this phase does not have instructions.
        """
        return self[1]


class TestCaseHelp(tuple):
    def __new__(cls,
                phase_helps: iter):
        """
        :type phase_helps: [TestCasePhaseHelp]
        """
        return tuple.__new__(cls, (list(phase_helps),))

    @property
    def phase_helps(self) -> list:
        """
        :type: [TestCasePhaseHelp]
        """
        return self[0]

    @property
    def phase_name_2_phase_help(self) -> dict:
        """
        :type: str -> TestCasePhaseHelp
        """
        return dict(map(lambda ph_help: (ph_help.name, ph_help),
                        self.phase_helps))


class TestSuiteSectionHelp(tuple):
    def __new__(cls,
                name: str):
        return tuple.__new__(cls, (name,))

    @property
    def name(self) -> str:
        return self[0]


class TestSuiteHelp(tuple):
    def __new__(cls,
                test_suite_section_helps: iter):
        return tuple.__new__(cls, (list(test_suite_section_helps),))

    @property
    def section_helps(self) -> list:
        return self[0]


class MainProgramHelp(tuple):
    def __new__(cls):
        return tuple.__new__(cls, ())


class ApplicationHelp(tuple):
    def __new__(cls,
                main_program_help: MainProgramHelp,
                test_case_help: TestCaseHelp,
                test_suite_help: TestSuiteHelp):
        return tuple.__new__(cls, (main_program_help,
                                   test_case_help,
                                   test_suite_help))

    @property
    def main_program_help(self) -> MainProgramHelp:
        return self[0]

    @property
    def test_case_help(self) -> TestCaseHelp:
        return self[1]

    @property
    def test_suite_help(self) -> TestSuiteHelp:
        return self[2]
