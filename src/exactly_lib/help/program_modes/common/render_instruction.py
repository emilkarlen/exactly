import types

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.render.doc_utils import synopsis_section, description_section
from exactly_lib.help.render.see_also_section import see_also_sections
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment, \
    ArticleContentsConstructor, \
    SectionContentsConstructorFromArticleContentsConstructor
from exactly_lib.util.textformat.structure import document as doc, lists
from exactly_lib.util.textformat.structure import structures as docs

LIST_INDENT = 2

BLANK_LINE_BETWEEN_ELEMENTS = lists.Separations(1, 0)


class InstructionDocArticleContentsConstructor(ArticleContentsConstructor):
    def __init__(self, documentation: InstructionDocumentation):
        self.documentation = documentation

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
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
        abstract_paragraphs = docs.paras(self.documentation.single_line_description())
        return doc.ArticleContents(abstract_paragraphs,
                                   doc.SectionContents([], sub_sections))


class InstructionDocSectionContentsConstructor(SectionContentsConstructorFromArticleContentsConstructor):
    def __init__(self, documentation: InstructionDocumentation):
        super().__init__(InstructionDocArticleContentsConstructor(documentation))


def instruction_set_list_item(description: InstructionDocumentation,
                              name_2_name_text_fun: types.FunctionType) -> lists.HeaderContentListItem:
    """
    :type name_2_name_text_fun: `str` -> `Text`
    """
    description_para = docs.para(description.single_line_description())
    return docs.list_item(name_2_name_text_fun(description.instruction_name()),
                          [description_para])
