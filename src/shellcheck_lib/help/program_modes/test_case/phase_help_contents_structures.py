from shellcheck_lib.document.syntax import phase_name_in_phase_syntax
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseHelp, \
    TestCasePhaseInstructionSet
from shellcheck_lib.help.utils.description import Description
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.paragraph import para


class PhaseSequenceInfo(tuple):
    def __new__(cls,
                preceding_phase: list,
                succeeding_phase: list):
        """
        :param preceding_phase: [ParagraphItem]
        :param succeeding_phase: [ParagraphItem]
        """
        return tuple.__new__(cls, (preceding_phase, succeeding_phase))

    @property
    def preceding_phase(self) -> list:
        return self[0]

    @property
    def succeeding_phase(self) -> list:
        return self[1]


class TestCasePhaseHelpBase(TestCasePhaseHelp):
    def __init__(self,
                 name: str):
        super().__init__(name)
        self._name_as_header = phase_name_in_phase_syntax(name)

    def render(self) -> doc.SectionContents:
        purpose = self.purpose()
        mandatory_info = para('The %s phase is %s.' % (self._name_as_header,
                                                       'mandatory' if self.is_mandatory() else 'optional'))
        paras = [para(purpose.single_line_description)] + purpose.rest + [mandatory_info]
        return doc.SectionContents(paras, [])

    def purpose(self) -> Description:
        raise NotImplementedError()

    def is_mandatory(self) -> bool:
        raise NotImplementedError()

    def sequence_info(self) -> PhaseSequenceInfo:
        raise NotImplementedError()


class TestCasePhaseHelpForPhaseWithInstructions(TestCasePhaseHelpBase):
    def __init__(self,
                 name: str,
                 instruction_set: TestCasePhaseInstructionSet):
        """
        :param instruction_set: None if this phase does not have instructions.
        """
        super().__init__(name)
        self._instruction_set = instruction_set

    @property
    def is_phase_with_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> TestCasePhaseInstructionSet:
        return self._instruction_set


class TestCasePhaseHelpForPhaseWithoutInstructions(TestCasePhaseHelpBase):
    def __init__(self,
                 name: str):
        super().__init__(name)

    @property
    def is_phase_with_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> TestCasePhaseInstructionSet:
        return None
