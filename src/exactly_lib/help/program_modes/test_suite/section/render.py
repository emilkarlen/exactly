from exactly_lib.help.program_modes.common.renderers import instruction_set_list
from exactly_lib.help.program_modes.common.section_documentation_renderer import SectionDocumentationRendererBase
from exactly_lib.help.program_modes.test_suite.section.common import TestSuiteSectionDocumentation
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.rendering.see_also_section import see_also_sections
from exactly_lib.help_texts.cross_reference_id import TestSuiteSectionInstructionCrossReference
from exactly_lib.help_texts.test_suite.section_names import DEFAULT_SECTION_NAME
from exactly_lib.help_texts.test_suite.section_names import SECTION_CONCEPT_NAME
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.utils import transform_list_to_table


class TestSuiteSectionDocumentationRenderer(SectionDocumentationRendererBase):
    def __init__(self, tss_doc: TestSuiteSectionDocumentation):
        super().__init__(tss_doc, SECTION_CONCEPT_NAME)
        self._doc = tss_doc

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        purpose = self._doc.purpose()
        mandatory_info = self._mandatory_info_para()
        paras = ([docs.para(purpose.single_line_description)] +
                 purpose.rest +
                 [mandatory_info] +
                 self._default_section_info(DEFAULT_SECTION_NAME))
        sections = []
        self._add_section_for_contents_description(sections)
        self._add_section_for_see_also(environment, sections)
        self._add_section_for_instructions(environment, sections)

        return doc.SectionContents(paras, sections)

    def _add_section_for_contents_description(self, output: list):
        output.append(docs.section('Contents',
                                   self._doc.contents_description()))

    def _add_section_for_instructions(self,
                                      environment: RenderingEnvironment,
                                      output: list):
        if self._doc.has_instructions:
            il = instruction_set_list(self._doc.instruction_set, self._cross_ref_text)
            if environment.render_simple_header_value_lists_as_tables:
                il = transform_list_to_table(il)
            output.append(docs.section('Instructions', [il]))

    def _add_section_for_see_also(self, environment: RenderingEnvironment, sections: list):
        sections.extend(see_also_sections(self._doc.see_also_items, environment))

    def _cross_ref_text(self, instr_name: str) -> docs.Text:
        return docs.cross_reference(instr_name,
                                    TestSuiteSectionInstructionCrossReference(self._doc.name.plain,
                                                                              instr_name),
                                    allow_rendering_of_visible_extra_target_text=False)
