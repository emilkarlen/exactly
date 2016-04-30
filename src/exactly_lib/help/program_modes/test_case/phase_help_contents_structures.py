from exactly_lib import program_info
from exactly_lib.help.program_modes.test_case.contents_structure import TestCasePhaseDocumentation, \
    TestCasePhaseInstructionSet
from exactly_lib.help.program_modes.test_case.render.instruction_set import instruction_set_list
from exactly_lib.help.utils.formatting import SectionName
from exactly_lib.help.utils.render import RenderingEnvironment, cross_reference_list, transform_list_to_table
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


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
        The names of the special environment variables that are available in the phase.
        :return: [str]
        """
        return self[1]


class TestCasePhaseDocumentationBase(TestCasePhaseDocumentation):
    def __init__(self,
                 name: str):
        super().__init__(name)
        self._phase_name = SectionName(name)

    def render(self, environment: RenderingEnvironment) -> doc.SectionContents:
        purpose = self.purpose()
        mandatory_info = self._mandatory_info_para()
        paras = ([docs.para(purpose.single_line_description)] +
                 purpose.rest +
                 [mandatory_info])
        sections = []
        self._add_section_for_contents_description(sections)
        self._add_section_for_phase_sequence_description(sections)
        self._add_section_for_environment(sections)
        self._add_section_for_see_also(environment, sections)
        self._add_section_for_instructions(environment, sections)

        return doc.SectionContents(paras, sections)

    def _mandatory_info_para(self):
        return docs.para('The {0} phase is {1}.'.format(self.name,
                                                        'mandatory' if self.is_mandatory() else 'optional'))

    def _add_section_for_contents_description(self, sections: list):
        sections.append(docs.section('Contents',
                                     self.contents_description()))

    def _add_section_for_phase_sequence_description(self, sections: list):
        si = self.sequence_info()
        sections.append(docs.section('Phase sequence',
                                     si.preceding_phase + si.succeeding_phase))

    def _add_section_for_environment(self, sections: list):
        eei = self.execution_environment_info()
        paragraphs = []
        if eei.pwd_at_start_of_phase:
            paragraphs.extend(eei.pwd_at_start_of_phase)
        if eei.environment_variables:
            paragraphs.extend([docs.para('The following environment variables are set:'),
                               self._environment_variables_list(eei.environment_variables)])
        else:
            paragraphs.append(docs.para('No extra environment variables have been set.'))
        sections.append(docs.section('Environment', paragraphs))

    @staticmethod
    def _environment_variables_list(environment_variable_names: list) -> ParagraphItem:
        return docs.simple_header_only_list(environment_variable_names,
                                            lists.ListType.ITEMIZED_LIST)

    def _add_section_for_instructions(self,
                                      environment: RenderingEnvironment,
                                      sections: list):
        if self.is_phase_with_instructions:
            il = instruction_set_list(self.instruction_set)
            if environment.render_simple_header_value_lists_as_tables:
                il = transform_list_to_table(il)
            sections.append(docs.section('Instructions', [il]))

    def _add_section_for_see_also(self, environment: RenderingEnvironment, sections: list):
        if self.see_also:
            cross_ref_list = cross_reference_list(self.see_also, environment)
            sections.append(docs.section('See also', [cross_ref_list]))

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
        return [docs.para('Consists of zero or more instructions.')] + self.instruction_purpose_description()

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
