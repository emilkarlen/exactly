from exactly_lib.help.program_modes.common.section_documentation_renderer import SectionDocumentationConstructorBase
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import TestCasePhaseDocumentation
from exactly_lib.help.render.see_also_section import see_also_sections
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.doc_format import syntax_text, instruction_name_text
from exactly_lib.help_texts.test_case.phase_names_plain import SECTION_CONCEPT_NAME, ACT_PHASE_NAME
from exactly_lib.test_case.phase_identifier import DEFAULT_PHASE
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


class TestCasePhaseDocumentationConstructor(SectionDocumentationConstructorBase):
    def __init__(self, tcp_doc: TestCasePhaseDocumentation):
        super().__init__(tcp_doc, SECTION_CONCEPT_NAME)
        self.doc = tcp_doc

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        purpose = self.doc.purpose()
        abstract_paras = docs.paras(purpose.single_line_description)

        return doc.ArticleContents(abstract_paras,
                                   self._section_contents(environment,
                                                          purpose.rest))

    def _section_contents(self,
                          environment: ConstructionEnvironment,
                          purpose_rest_paras: list) -> doc.SectionContents:
        mandatory_info = self._mandatory_info_para()
        paras = (purpose_rest_paras +
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
        sections.append(doc.Section(self.CONTENTS_HEADER,
                                    section_contents))

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

    def _instruction_cross_ref_text(self, instr_name: str) -> docs.Text:
        return docs.cross_reference(instruction_name_text(instr_name),
                                    TestCasePhaseInstructionCrossReference(self.doc.name.plain,
                                                                           instr_name),
                                    allow_rendering_of_visible_extra_target_text=False)

    @staticmethod
    def _environment_variables_list(environment_variable_names: list) -> ParagraphItem:
        return docs.simple_header_only_list(map(syntax_text, environment_variable_names),
                                            lists.ListType.ITEMIZED_LIST)

    def _add_section_for_see_also(self, environment: ConstructionEnvironment, sections: list):
        sections += see_also_sections(self.doc.see_also_targets, environment)
