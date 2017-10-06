import types

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.utils.doc_utils import synopsis_section, description_section
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.rendering.see_also_section import see_also_sections
from exactly_lib.util.textformat.structure import document as doc, lists
from exactly_lib.util.textformat.structure.structures import para

LIST_INDENT = 2

BLANK_LINE_BETWEEN_ELEMENTS = lists.Separations(1, 0)


class InstructionManPageRenderer(SectionContentsRenderer):
    def __init__(self,
                 documentation: InstructionDocumentation):
        self.documentation = documentation

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        documentation = self.documentation
        sub_sections = []
        if documentation.invokation_variants():
            sub_sections.append(synopsis_section(
                invokation_variants_content(documentation.instruction_name(),
                                            documentation.invokation_variants(),
                                            documentation.syntax_element_descriptions())))
        main_description_rest = documentation.main_description_rest()
        if main_description_rest:
            sub_sections.append(description_section(doc.SectionContents(main_description_rest)))
        sub_sections += see_also_sections(documentation.see_also_targets(), environment,
                                          uppercase_title=True)
        prelude_paragraphs = [para(documentation.single_line_description())]
        return doc.SectionContents(prelude_paragraphs,
                                   sub_sections)


def instruction_set_list_item(description: InstructionDocumentation,
                              name_2_name_text_fun: types.FunctionType) -> lists.HeaderContentListItem:
    """
    :type name_2_name_text_fun: `str` -> `Text`
    """
    description_para = para(description.single_line_description())
    return lists.HeaderContentListItem(name_2_name_text_fun(description.instruction_name()),
                                       [description_para])
