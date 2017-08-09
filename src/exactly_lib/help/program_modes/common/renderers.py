import types

from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation, SectionInstructionSet
from exactly_lib.help.program_modes.common.render_instruction import instruction_set_list_item
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.textformat.structure import document as doc, lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


class SectionInstructionSetRenderer(SectionContentsRenderer):
    def __init__(self, instruction_set: SectionInstructionSet):
        self.instruction_set = instruction_set

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        _instruction_list = instruction_set_list(self.instruction_set, docs.text)
        return doc.SectionContents([_instruction_list], [])


def instruction_set_list(instruction_set: SectionInstructionSet,
                         name_2_name_text_fun: types.FunctionType) -> lists.HeaderContentList:
    instruction_list_items = []
    for description in instruction_set.instruction_descriptions:
        list_item = instruction_set_list_item(description, name_2_name_text_fun)
        instruction_list_items.append(list_item)
    return lists.HeaderContentList(instruction_list_items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0))


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
