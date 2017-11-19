from exactly_lib.help.program_modes.common.renderers import instruction_set_list
from exactly_lib.help.program_modes.common.section_documentation_renderer import SectionDocumentationRendererBase
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import TestCasePhaseDocumentation
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.rendering.see_also_section import see_also_sections
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.test_case.phase_names_plain import SECTION_CONCEPT_NAME, ACT_PHASE_NAME
from exactly_lib.test_case.phase_identifier import DEFAULT_PHASE
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.utils import transform_list_to_table


class TestCasePhaseDocumentationRenderer(SectionDocumentationRendererBase):
    def __init__(self, tcp_doc: TestCasePhaseDocumentation):
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
            if self.doc.name.plain == ACT_PHASE_NAME:
                # FIXME Remove setting of env vars for the act phase.
                paragraphs.append(docs.para('NOTE: In future versions, '
                                            'these environment variables will not be available!'))
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
        sections += see_also_sections(self.doc.see_also_targets, environment)
