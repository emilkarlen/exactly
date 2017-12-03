from exactly_lib.help.program_modes.common.section_documentation_renderer import SectionDocumentationConstructorBase
from exactly_lib.help.program_modes.test_suite.section.common import TestSuiteSectionDocumentation
from exactly_lib.help.render.see_also_section import see_also_sections
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestSuiteSectionInstructionCrossReference
from exactly_lib.help_texts.doc_format import instruction_name_text
from exactly_lib.help_texts.test_suite.section_names import DEFAULT_SECTION_NAME
from exactly_lib.help_texts.test_suite.section_names import SECTION_CONCEPT_NAME
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class TestSuiteSectionDocumentationConstructor(SectionDocumentationConstructorBase):
    def __init__(self, tss_doc: TestSuiteSectionDocumentation):
        super().__init__(tss_doc, SECTION_CONCEPT_NAME)
        self._doc = tss_doc

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        purpose = self._doc.purpose()
        abstract_paras = docs.paras(purpose.single_line_description)
        return doc.ArticleContents(abstract_paras,
                                   self._section_contents(environment,
                                                          purpose.rest))

    def _section_contents(self,
                          environment: ConstructionEnvironment,
                          purpose_rest: list) -> doc.SectionContents:
        mandatory_info = self._mandatory_info_para()
        paras = (purpose_rest +
                 [mandatory_info] +
                 self._default_section_info(DEFAULT_SECTION_NAME))
        sections = []
        self._add_section_for_contents_description(sections)
        self._add_section_for_see_also(environment, sections)
        self._add_section_for_instructions(environment, sections)

        return doc.SectionContents(paras, sections)

    def _add_section_for_contents_description(self, output: list):
        output.append(docs.section(self.CONTENTS_HEADER,
                                   self._doc.contents_description()))

    def _add_section_for_see_also(self, environment: ConstructionEnvironment, sections: list):
        sections += see_also_sections(self._doc.see_also_targets, environment)

    def _instruction_cross_ref_text(self, instr_name: str) -> docs.Text:
        return docs.cross_reference(instruction_name_text(instr_name),
                                    TestSuiteSectionInstructionCrossReference(self._doc.name.plain,
                                                                              instr_name),
                                    allow_rendering_of_visible_extra_target_text=False)
