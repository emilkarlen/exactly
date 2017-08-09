from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.help.program_modes.common.renderers import instruction_set_list
from exactly_lib.help.program_modes.common.section_documentation_renderer import SectionDocumentationRendererBase
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.rendering.see_also_section import see_also_sections
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.test_case.phase_names_plain import SECTION_CONCEPT_NAME
from exactly_lib.test_case.phase_identifier import DEFAULT_PHASE
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.utils import transform_list_to_table


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


class TestCasePhaseDocumentationBase(SectionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def sequence_info(self) -> PhaseSequenceInfo:
        raise NotImplementedError()

    def contents_description(self) -> doc.SectionContents:
        raise NotImplementedError()

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        raise NotImplementedError()

    def render(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return self.renderer().apply(environment)

    def renderer(self) -> SectionContentsRenderer:
        return TestCasePhaseDocumentationRenderer(self)


class TestCasePhaseDocumentationForPhaseWithInstructions(TestCasePhaseDocumentationBase):
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


class TestCasePhaseDocumentationForPhaseWithoutInstructions(TestCasePhaseDocumentationBase):
    def __init__(self,
                 name: str):
        super().__init__(name)

    @property
    def has_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> SectionInstructionSet:
        return None


class TestCasePhaseDocumentationRenderer(SectionDocumentationRendererBase):
    def __init__(self, tcp_doc: TestCasePhaseDocumentationBase):
        super().__init__(tcp_doc, SECTION_CONCEPT_NAME)
        self.doc = tcp_doc

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        purpose = self.doc.purpose()
        mandatory_info = self._mandatory_info_para()
        paras = ([docs.para(purpose.single_line_description)] +
                 purpose.rest +
                 [mandatory_info] +
                 self._default_section_info(DEFAULT_PHASE.section_name))
        sections = []
        self._add_section_for_contents_description(sections)
        self._add_section_for_phase_sequence_description(sections)
        self._add_section_for_environment(sections)
        self._add_section_for_see_also(environment, sections)
        self._add_section_for_instructions(environment, sections)

        return doc.SectionContents(paras, sections)

    def _add_section_for_contents_description(self, sections: list):
        section_contents = self.doc.contents_description()
        sections.append(doc.Section(docs.text('Contents'), section_contents))

    def _add_section_for_phase_sequence_description(self, sections: list):
        si = self.doc.sequence_info()
        sections.append(docs.section('Phase execution order',
                                     si.prelude + si.preceding_phase + si.succeeding_phase))

    def _add_section_for_environment(self, sections: list):
        eei = self.doc.execution_environment_info()
        paragraphs = []
        if eei.cwd_at_start_of_phase:
            paragraphs.extend(eei.cwd_at_start_of_phase)
        if eei.environment_variables:
            paragraphs.extend([docs.para('The following environment variables are set:'),
                               self._environment_variables_list(eei.environment_variables)])
        paragraphs.extend(eei.prologue)
        if paragraphs:
            sections.append(docs.section('Environment', paragraphs))

    def _cross_ref_text(self, instr_name: str) -> docs.Text:
        return docs.cross_reference(instr_name,
                                    TestCasePhaseInstructionCrossReference(self.doc.name.plain,
                                                                           instr_name),
                                    allow_rendering_of_visible_extra_target_text=False)

    @staticmethod
    def _environment_variables_list(environment_variable_names: list) -> ParagraphItem:
        return docs.simple_header_only_list(environment_variable_names,
                                            lists.ListType.ITEMIZED_LIST)

    def _add_section_for_instructions(self,
                                      environment: RenderingEnvironment,
                                      sections: list):
        if self.doc.has_instructions:
            il = instruction_set_list(self.doc.instruction_set, self._cross_ref_text)
            if environment.render_simple_header_value_lists_as_tables:
                il = transform_list_to_table(il)
            sections.append(docs.section('Instructions', [il]))

    def _add_section_for_see_also(self, environment: RenderingEnvironment, sections: list):
        sections.extend(see_also_sections(self.doc.see_also_items, environment))
