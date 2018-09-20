from typing import List

from exactly_lib.definitions.doc_format import instruction_name_text
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.common.renderers import default_section_para, instruction_set_constructor
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor
from exactly_lib.util.textformat.structure import structures as docs


class SectionDocumentationConstructorBase(ArticleContentsConstructor):
    CONTENTS_HEADER = docs.text('Contents')

    def __init__(self,
                 section_documentation: SectionDocumentation,
                 section_concept_name: str,
                 instructions_section_header: docs.Text):
        self.__section_documentation = section_documentation
        self.__section_concept_name = section_concept_name
        self.__instructions_section_header = instructions_section_header

    def _default_section_info(self, default_section_name: str) -> List[docs.ParagraphItem]:
        ret_val = []
        if self.__section_documentation.name.plain == default_section_name:
            ret_val.append(default_section_para(self.__section_concept_name))
        return ret_val

    def _instruction_cross_ref_text(self, instr_name: str) -> docs.Text:
        return docs.cross_reference(
            instruction_name_text(instr_name),
            self.__section_documentation.section_info.instruction_cross_reference_target(instr_name),
            allow_rendering_of_visible_extra_target_text=False)

    def _add_section_for_instructions(self,
                                      environment: ConstructionEnvironment,
                                      output: List[docs.SectionItem]):
        if self.__section_documentation.has_instructions:
            renderer = instruction_set_constructor(
                self.__section_documentation.instruction_set,
                self._instruction_cross_ref_text,
                instruction_group_by=self.__section_documentation.instruction_group_by)
            output.append(docs.Section(self.__instructions_section_header,
                                       renderer.apply(environment)))
