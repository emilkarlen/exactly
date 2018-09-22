from typing import Callable, List

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.render.doc_utils import synopsis_section, description_section
from exactly_lib.help.render.see_also import see_also_sections
from exactly_lib.util.textformat.constructor import sections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor, SectionContentsConstructor
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
        sub_sections += self._main_description_rest_sections()
        sub_sections += see_also_sections(documentation.see_also_targets(), environment,
                                          uppercase_title=True)
        abstract_paragraphs = docs.paras(self.documentation.single_line_description())
        return doc.ArticleContents(abstract_paragraphs,
                                   doc.SectionContents([], sub_sections))

    def _main_description_rest_sections(self) -> List[docs.Section]:
        d = self.documentation
        ip = list(d.main_description_rest())
        ss = list(d.main_description_rest_sub_sections())
        if not (ip or ss):
            return []
        section = description_section(
            doc.SectionContents(ip,
                                ss)
        )
        return [section]


def instruction_doc_section_contents_constructor(documentation: InstructionDocumentation) -> SectionContentsConstructor:
    return sections.contents_from_article_contents(InstructionDocArticleContentsConstructor(documentation))


def instruction_set_list_item(description: InstructionDocumentation,
                              name_2_name_text_fun: Callable[[str], docs.Text]) -> lists.HeaderContentListItem:
    description_para = docs.para(description.single_line_description())
    return docs.list_item(name_2_name_text_fun(description.instruction_name()),
                          [description_para])
