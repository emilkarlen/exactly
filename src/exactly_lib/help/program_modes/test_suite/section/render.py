from exactly_lib.help.program_modes.common.section_documentation_renderer import SectionDocumentationRendererBase
from exactly_lib.help.program_modes.test_suite.section.common import TestSuiteSectionDocumentation
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.rendering.see_also_section import see_also_sections
from exactly_lib.help_texts.cross_reference_id import TestSuiteSectionInstructionCrossReference
from exactly_lib.help_texts.test_suite.section_names import DEFAULT_SECTION_NAME
from exactly_lib.help_texts.test_suite.section_names import SECTION_CONCEPT_NAME
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


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

    def _add_section_for_see_also(self, environment: RenderingEnvironment, sections: list):
        sections += see_also_sections(self._doc.see_also_targets, environment)

    def _instruction_cross_ref_text(self, instr_name: str) -> docs.Text:
        return docs.cross_reference(instr_name,
                                    TestSuiteSectionInstructionCrossReference(self._doc.name.plain,
                                                                              instr_name),
                                    allow_rendering_of_visible_extra_target_text=False)
