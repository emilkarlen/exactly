import shellcheck_lib.util.textformat.structure.structures
from shellcheck_lib.document.syntax import section_header
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseDocumentation, \
    TestCasePhaseInstructionSet
from shellcheck_lib.help.program_modes.test_case.render.instruction_set import instruction_set_list
from shellcheck_lib.help.utils.description import Description
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.paragraph import para, text


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


class ExecutionEnvironmentInfo(tuple):
    def __new__(cls,
                pwd_at_start_of_phase: list,
                environment_variables: list):
        """
        :param pwd_at_start_of_phase: [ParagraphItem]
        :param environment_variables: [str]
        """
        return tuple.__new__(cls, (pwd_at_start_of_phase,
                                   environment_variables))

    @property
    def pwd_at_start_of_phase(self) -> list:
        """
        Description of the Present Workding Directory, at the start of the phase.
        :return: [ParagraphItem]
        """
        return self[0]

    @property
    def environment_variables(self) -> list:
        """
        The names of the shellcheck environment variables that are available in the phase.
        :return: [str]
        """
        return self[1]


class TestCasePhaseDocumentationBase(TestCasePhaseDocumentation):
    def __init__(self,
                 name: str):
        super().__init__(name)
        self._name_as_header = section_header(name)

    def render(self) -> doc.SectionContents:
        # TODO clean this method up
        purpose = self.purpose()
        mandatory_info = para('The {0} phase is {1}.'.format(self.name,
                                                             'mandatory' if self.is_mandatory() else 'optional'))
        paras = ([para(purpose.single_line_description)] +
                 purpose.rest +
                 [mandatory_info] +
                 self.contents_description())
        eei = self.execution_environment_info()
        sections = []
        if eei.pwd_at_start_of_phase:
            sections.append(doc.Section(text('Present Working Directory'),
                                        doc.SectionContents(eei.pwd_at_start_of_phase, [])))
        if eei.environment_variables:
            ev_list = shellcheck_lib.util.textformat.structure.structures.simple_header_only_list(
                eei.environment_variables,
                lists.ListType.ITEMIZED_LIST)
            sections.append(doc.Section(text('Environment Variables (TODO check this)'),
                                        doc.SectionContents([ev_list],
                                                            [])))
        if self.is_phase_with_instructions:
            il = instruction_set_list(self.instruction_set)
            sections.append(doc.Section(text('Instructions'),
                                        doc.SectionContents([il], [])))
        return doc.SectionContents(paras, sections)

    def purpose(self) -> Description:
        raise NotImplementedError()

    def is_mandatory(self) -> bool:
        raise NotImplementedError()

    def sequence_info(self) -> PhaseSequenceInfo:
        raise NotImplementedError()

    def contents_description(self) -> list:
        """
        :return: [ParagraphItem]
        """
        raise NotImplementedError()

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        raise NotImplementedError()


class TestCasePhaseDocumentationForPhaseWithInstructions(TestCasePhaseDocumentationBase):
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

    def contents_description(self) -> list:
        return [para('Consists of a sequence of instructions.')] + self.instruction_purpose_description()

    def instruction_purpose_description(self) -> list:
        """
        :return: [ParagraphItem]
        """
        raise NotImplementedError()


class TestCasePhaseDocumentationForPhaseWithoutInstructions(TestCasePhaseDocumentationBase):
    def __init__(self,
                 name: str):
        super().__init__(name)

    @property
    def is_phase_with_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> TestCasePhaseInstructionSet:
        return None
