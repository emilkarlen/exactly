from typing import List

from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.test_case.phase_names_plain import SECTION_CONCEPT_NAME
from exactly_lib.help.program_modes.common import contents as common_contents
from exactly_lib.help.program_modes.common.section_documentation_renderer import SectionDocumentationConstructorBase
from exactly_lib.help.program_modes.test_case.contents_structure.phase_documentation import TestCasePhaseDocumentation
from exactly_lib.help.render.see_also import see_also_sections
from exactly_lib.test_case.phase_identifier import DEFAULT_PHASE
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


class TestCasePhaseDocumentationConstructor(SectionDocumentationConstructorBase):
    def __init__(self, tcp_doc: TestCasePhaseDocumentation):
        super().__init__(tcp_doc, SECTION_CONCEPT_NAME,
                         common_contents.INSTRUCTIONS_SECTION_HEADER)
        self.doc = tcp_doc

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        purpose = self.doc.purpose()
        abstract_paras = docs.paras(purpose.single_line_description)

        return doc.ArticleContents(abstract_paras,
                                   self._section_contents(environment,
                                                          purpose.rest))

    def _section_contents(self,
                          environment: ConstructionEnvironment,
                          purpose_rest_paras: List[docs.ParagraphItem]) -> doc.SectionContents:
        paras = (purpose_rest_paras +
                 self._default_section_info(DEFAULT_PHASE.section_name))
        sections = []
        self._add_section_for_contents_description(sections)
        self._add_section_for_phase_sequence_description(sections)
        self._add_section_for_environment(sections)
        self._add_section_for_see_also(environment, sections)
        self._add_section_for_instructions(environment, sections)

        return doc.SectionContents(paras, sections)

    def _add_section_for_contents_description(self, output: List[docs.SectionItem]):
        section_contents = self.doc.contents_description()
        output.append(doc.Section(self.CONTENTS_HEADER,
                                  section_contents))

    def _add_section_for_phase_sequence_description(self, output: List[docs.SectionItem]):
        si = self.doc.sequence_info()
        output.append(docs.section('Phase execution order',
                                   si.prelude + si.preceding_phase + si.succeeding_phase))

    def _add_section_for_environment(self, output: List[docs.SectionItem]):
        list_items = []
        list_items += self._current_directory_items()
        list_items += self._environment_variables_items()
        list_items += self._timeout_items()
        list_items += self.doc.execution_environment_info().custom_items
        if list_items:
            properties_list = docs.simple_list_with_space_between_elements_and_content(list_items,
                                                                                       lists.ListType.ITEMIZED_LIST)
            output.append(docs.section('Environment',
                                       [properties_list]))

    def _current_directory_items(self) -> List[lists.HeaderContentListItem]:
        eei = self.doc.execution_environment_info()
        if eei.cwd_at_start_of_phase:
            list_item = docs.list_item(
                '{cd:/u}'.format(cd=concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO.name),
                eei.cwd_at_start_of_phase
            )
            return [list_item]
        else:
            return []

    def _environment_variables_items(self) -> List[lists.HeaderContentListItem]:
        eei = self.doc.execution_environment_info()
        paragraphs = []
        paragraphs += eei.environment_variables_prologue
        if paragraphs:
            list_item = docs.list_item(
                '{ev:s/u}'.format(ev=concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.name),
                paragraphs
            )
            return [list_item]
        else:
            return []

    def _timeout_items(self) -> List[lists.HeaderContentListItem]:
        eei = self.doc.execution_environment_info()
        paragraphs = []
        paragraphs += eei.timeout_prologue
        if paragraphs:
            list_item = docs.list_item(
                '{timeout:/u}'.format(timeout=concepts.TIMEOUT_CONCEPT_INFO.name),
                paragraphs
            )
            return [list_item]
        else:
            return []

    @staticmethod
    def _environment_variables_list(environment_variable_names: List[str]) -> ParagraphItem:
        return docs.simple_header_only_list(map(syntax_text, environment_variable_names),
                                            lists.ListType.ITEMIZED_LIST)

    def _add_section_for_see_also(self, environment: ConstructionEnvironment, output: List[docs.SectionItem]):
        output += see_also_sections(self.doc.see_also_targets, environment)
