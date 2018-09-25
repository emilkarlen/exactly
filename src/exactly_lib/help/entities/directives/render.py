from exactly_lib.help.entities.directives.contents_structure import DirectiveDocumentation
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.render.doc_utils import synopsis_section, description_section
from exactly_lib.help.render.see_also import see_also_sections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class IndividualDirectiveConstructor(ArticleContentsConstructor):
    def __init__(self, documentation: DirectiveDocumentation):
        self.documentation = documentation
        self.rendering_environment = None

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        documentation = self.documentation
        sub_sections = []
        if documentation.invokation_variants():
            sub_sections.append(synopsis_section(
                invokation_variants_content(documentation.singular_name(),
                                            documentation.invokation_variants(),
                                            documentation.syntax_element_descriptions())))
        description = self.documentation.description()
        if description is not None:
            sub_sections.append(description_section(description))

        sub_sections += see_also_sections(documentation.see_also_targets(), environment,
                                          uppercase_title=True)

        abstract_paragraphs = docs.paras(self.documentation.single_line_description())
        return doc.ArticleContents(abstract_paragraphs,
                                   doc.SectionContents([], sub_sections))
