import types

from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation, SectionInstructionSet
from exactly_lib.help.program_modes.common.render_instruction import instruction_set_list_item
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, ParagraphItemsRenderer, \
    SectionContentsRendererFromParagraphItemsRenderer
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.utils import transform_list_to_table


class InstructionSetSummaryRenderer(ParagraphItemsRenderer):
    def __init__(self,
                 instruction_set: SectionInstructionSet,
                 name_2_name_text_fun: types.FunctionType = docs.text):
        self.instruction_set = instruction_set
        self.name_2_name_text_fun = name_2_name_text_fun

    def apply(self, environment: RenderingEnvironment) -> list:
        paragraph_item = self.instruction_set_list()
        if environment.render_simple_header_value_lists_as_tables:
            paragraph_item = transform_list_to_table(paragraph_item)
        return [paragraph_item]

    def instruction_set_list(self) -> lists.HeaderContentList:
        instruction_list_items = []
        for description in self.instruction_set.instruction_descriptions:
            list_item = instruction_set_list_item(description, self.name_2_name_text_fun)
            instruction_list_items.append(list_item)
        return lists.HeaderContentList(instruction_list_items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_indent_spaces=0))


class SectionInstructionSetRenderer(SectionContentsRendererFromParagraphItemsRenderer):
    def __init__(self, instruction_set: SectionInstructionSet,
                 name_2_name_text_fun: types.FunctionType = docs.text):
        super().__init__([InstructionSetSummaryRenderer(instruction_set,
                                                        name_2_name_text_fun)])


def sections_short_list(sections: list,
                        default_section_name: str = '',
                        section_concept_name: str = 'section') -> ParagraphItem:
    """
    :param sections: List[`SectionDocumentation`]
    """

    def add_default_info(section: SectionDocumentation, output: list):
        if section.name.plain == default_section_name:
            output.append(default_section_para(section_concept_name))

    items = []
    for section in sections:
        assert isinstance(section, SectionDocumentation)
        paras = [docs.para(section.purpose().single_line_description)]
        add_default_info(section, paras)
        items.append(docs.list_item(section.name.syntax, paras))
    return docs.simple_list_with_space_between_elements_and_content(
        items,
        lists.ListType.VARIABLE_LIST)


def default_section_para(section_concept_name: str = 'section') -> docs.ParagraphItem:
    return docs.para(_DEFAULT_SECTION_STRING.format(section_concept_name=section_concept_name))


_DEFAULT_SECTION_STRING = """This is the default {section_concept_name}."""
