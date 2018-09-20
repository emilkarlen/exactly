from typing import List

from exactly_lib.definitions.test_suite.section_names_plain import DEFAULT_SECTION_NAME
from exactly_lib.definitions.test_suite.section_names_plain import SECTION_CONCEPT_NAME
from exactly_lib.help.program_modes.common.section_documentation_renderer import SectionDocumentationConstructorBase
from exactly_lib.help.program_modes.test_suite.contents_structure.section_documentation import \
    TestSuiteSectionDocumentation
from exactly_lib.help.render.see_also import see_also_sections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class TestSuiteSectionDocumentationConstructor(SectionDocumentationConstructorBase):
    def __init__(self,
                 tss_doc: TestSuiteSectionDocumentation):
        super().__init__(tss_doc, SECTION_CONCEPT_NAME, tss_doc.instructions_section_header())
        self._doc = tss_doc

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        purpose = self._doc.purpose()
        abstract_paras = docs.paras(purpose.single_line_description)
        return doc.ArticleContents(abstract_paras,
                                   self._section_contents(environment,
                                                          purpose.rest))

    def _section_contents(self,
                          environment: ConstructionEnvironment,
                          purpose_rest: List[docs.ParagraphItem]) -> doc.SectionContents:
        paras = (purpose_rest +
                 self._default_section_info(DEFAULT_SECTION_NAME))
        sections = []
        self._add_section_for_contents_description(sections)
        self._add_section_for_see_also(environment, sections)
        self._add_section_for_instructions(environment, sections)

        return doc.SectionContents(paras, sections)

    def _add_section_for_contents_description(self, output: List[docs.SectionItem]):
        output.append(docs.Section(self.CONTENTS_HEADER,
                                   self._doc.contents_description()))

    def _add_section_for_see_also(self, environment: ConstructionEnvironment, sections: List[docs.SectionItem]):
        sections += see_also_sections(self._doc.see_also_targets, environment)
