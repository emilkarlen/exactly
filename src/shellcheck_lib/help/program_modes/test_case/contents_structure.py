from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation
from shellcheck_lib.util.textformat.structure import document as doc


class TestCasePhaseInstructionSet(tuple):
    def __new__(cls,
                instruction_descriptions: iter):
        """
        :type instruction_descriptions: [Description]
        """
        description_list = list(instruction_descriptions)
        description_list.sort(key=InstructionDocumentation.instruction_name)
        return tuple.__new__(cls, (description_list,))

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


class TestCasePhaseDocumentation:
    def __init__(self,
                 name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def render(self) -> doc.SectionContents:
        raise NotImplementedError()

    @property
    def is_phase_with_instructions(self) -> bool:
        raise NotImplementedError()

    @property
    def instruction_set(self) -> TestCasePhaseInstructionSet:
        """
        :return: None if this phase does not have instructions.
        """
        raise NotImplementedError()


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
