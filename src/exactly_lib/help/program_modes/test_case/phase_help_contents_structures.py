from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class PhaseSequenceInfo(tuple):
    def __new__(cls,
                preceding_phase: list,
                succeeding_phase: list,
                prelude: iter = ()):
        """
        :param preceding_phase: [ParagraphItem]
        :param succeeding_phase: [ParagraphItem]
        :param prelude: [ParagraphItem]
        """
        return tuple.__new__(cls, (list(prelude), preceding_phase, succeeding_phase))

    @property
    def prelude(self) -> list:
        return self[0]

    @property
    def preceding_phase(self) -> list:
        return self[1]

    @property
    def succeeding_phase(self) -> list:
        return self[2]


class ExecutionEnvironmentInfo(tuple):
    def __new__(cls,
                cwd_at_start_of_phase: list,
                environment_variables: list,
                prologue: iter = ()):
        """
        :param cwd_at_start_of_phase: [ParagraphItem]
        :param environment_variables: [str]
        :param prologue: [`ParagraphItem`]
        """
        return tuple.__new__(cls, (cwd_at_start_of_phase,
                                   environment_variables,
                                   list(prologue)))

    @property
    def cwd_at_start_of_phase(self) -> list:
        """
        Description of the Present Working Directory, at the start of the phase.
        :rtype: [ParagraphItem]
        """
        return self[0]

    @property
    def environment_variables(self) -> list:
        """
        The names of the special environment variables that are available in the phase.
        :rtype: [str]
        """
        return self[1]

    @property
    def prologue(self) -> list:
        """
        :rtype: [ParagraphItem]
        """
        return self[2]


class TestCasePhaseDocumentation(SectionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def sequence_info(self) -> PhaseSequenceInfo:
        raise NotImplementedError()

    def contents_description(self) -> doc.SectionContents:
        raise NotImplementedError()

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        raise NotImplementedError()


class TestCasePhaseDocumentationForPhaseWithInstructions(TestCasePhaseDocumentation):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        """
        :param instruction_set: None if this phase does not have instructions.
        """
        super().__init__(name)
        self._instruction_set = instruction_set

    @property
    def has_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> SectionInstructionSet:
        return self._instruction_set

    def contents_description(self) -> doc.SectionContents:
        return docs.section_contents([docs.para('Consists of zero or more instructions.')] +
                                     self.instruction_purpose_description())

    def instruction_purpose_description(self) -> list:
        """
        :return: [ParagraphItem]
        """
        raise NotImplementedError()


class TestCasePhaseDocumentationForPhaseWithoutInstructions(TestCasePhaseDocumentation):
    def __init__(self,
                 name: str):
        super().__init__(name)

    @property
    def has_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> SectionInstructionSet:
        return None
