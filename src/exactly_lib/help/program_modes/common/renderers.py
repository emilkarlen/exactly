from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation, SectionInstructionSet
from exactly_lib.help.program_modes.common.render_instruction import instruction_set_list_item
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc, lists
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.structures import list_item, para, \
    simple_list_with_space_between_elements_and_content


class SectionDocumentationRenderer(SectionContentsRenderer):
    def __init__(self, section_documentation: SectionDocumentation):
        self.section_documentation = section_documentation

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return self.section_documentation.render(environment)


class SectionInstructionSetRenderer(SectionContentsRenderer):
    def __init__(self, instruction_set: SectionInstructionSet):
        self.instruction_set = instruction_set

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        _instruction_list = instruction_set_list(self.instruction_set)
        return doc.SectionContents([_instruction_list], [])


def instruction_set_list(instruction_set: SectionInstructionSet) -> lists.HeaderContentList:
    instruction_list_items = []
    for description in instruction_set.instruction_descriptions:
        list_item = instruction_set_list_item(description)
        instruction_list_items.append(list_item)
    return lists.HeaderContentList(instruction_list_items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0))


def sections_short_list(sections: list) -> ParagraphItem:
    items = []
    for section in sections:
        assert isinstance(section, SectionDocumentation)
        items.append(list_item(section.name.syntax,
                               [para(section.purpose().single_line_description)]))
    return simple_list_with_space_between_elements_and_content(
        items,
        lists.ListType.VARIABLE_LIST)