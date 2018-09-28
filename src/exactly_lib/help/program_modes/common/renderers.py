from typing import Sequence, List, Callable, Optional

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation, SectionInstructionSet, \
    InstructionGroup
from exactly_lib.help.program_modes.common.render_instruction import instruction_set_list_item
from exactly_lib.util.textformat.constructor import sections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.paragraph import ParagraphItemsConstructor
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.lists import ListType, HeaderContentListItem
from exactly_lib.util.textformat.utils import transform_list_to_table


class InstructionSetSummaryConstructor(ParagraphItemsConstructor):
    def __init__(self,
                 instruction_set: SectionInstructionSet,
                 name_2_name_text_fun: Callable[[str], docs.Text],
                 instruction_group_by: Optional[
                     Callable[[Sequence[InstructionDocumentation]], Sequence[InstructionGroup]]]):
        self.instruction_set = instruction_set
        self.name_2_name_text_fun = name_2_name_text_fun
        self.instruction_group_by = instruction_group_by

    def apply(self, environment: ConstructionEnvironment) -> List[ParagraphItem]:
        if self.instruction_group_by is None:
            paragraph_item = self.instruction_set_list(self.instruction_set.instruction_documentations,
                                                       environment)
        else:
            paragraph_item = self._grouped_instructions(environment)
        return [paragraph_item]

    def _grouped_instructions(self, environment: ConstructionEnvironment) -> ParagraphItem:
        items = []
        for group in self.instruction_group_by(self.instruction_set.instruction_documentations):
            items.append(docs.list_item(group.header,
                                        [
                                            self.instruction_set_list(group.instruction_documentations,
                                                                      environment)])
                         )
        return docs.simple_list_with_space_between_elements_and_content(items,
                                                                        ListType.ITEMIZED_LIST)

    def instruction_set_list(self,
                             instructions: Sequence[InstructionDocumentation],
                             environment: ConstructionEnvironment) -> ParagraphItem:
        instruction_list_items = [
            instruction_set_list_item(doc, self.name_2_name_text_fun)
            for doc in instructions
        ]
        instr_list = lists.HeaderContentList(instruction_list_items,
                                             lists.Format(lists.ListType.VARIABLE_LIST,
                                                          custom_indent_spaces=0))

        if environment.construct_simple_header_value_lists_as_tables:
            return transform_list_to_table(instr_list)
        else:
            return instr_list


def instruction_set_constructor(
        instruction_set: SectionInstructionSet,
        name_2_name_text_fun: Callable[[str], docs.Text] = docs.text,
        instruction_group_by:
        Optional[Callable[[Sequence[InstructionDocumentation]], Sequence[InstructionGroup]]] = None
) -> sections.SectionContentsConstructor:
    return sections.contents(
        InstructionSetSummaryConstructor(instruction_set,
                                         name_2_name_text_fun,
                                         instruction_group_by)
    )


def sections_short_list(sections: Sequence[SectionDocumentation],
                        default_section_name: str = '',
                        section_concept_name: str = 'section') -> ParagraphItem:
    def add_default_info(doc: SectionDocumentation, output: List[docs.ParagraphItem]):
        if doc.name.plain == default_section_name:
            output.append(default_section_para(section_concept_name))

    def list_item(doc: SectionDocumentation) -> HeaderContentListItem:
        paras = [docs.para(doc.purpose().single_line_description)]
        add_default_info(doc, paras)
        return docs.list_item(doc.syntax_name_cross_ref_text, paras)

    items = map(list_item, sections)
    return docs.simple_list_with_space_between_elements_and_content(
        items,
        lists.ListType.VARIABLE_LIST)


def default_section_para(section_concept_name: str = 'section') -> docs.ParagraphItem:
    return docs.para(_DEFAULT_SECTION_STRING.format(section_concept_name=section_concept_name))


_DEFAULT_SECTION_STRING = """This is the default {section_concept_name}."""
