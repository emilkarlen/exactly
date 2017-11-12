from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_paragraphs
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.rendering.see_also_section import see_also_sections
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class IndividualSyntaxElementRenderer(SectionContentsRenderer):
    def __init__(self, syntax_element: SyntaxElementDocumentation):
        self.syntax_element = syntax_element

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        initial_paragraphs = [docs.para(self.syntax_element.single_line_description())]
        initial_paragraphs += self.syntax_element.main_description_rest()
        initial_paragraphs += invokation_variants_paragraphs(None,
                                                             self.syntax_element.invokation_variants(),
                                                             self.syntax_element.syntax_element_descriptions())
        sub_sections = see_also_sections(self.syntax_element.see_also_targets(), environment,
                                         uppercase_title=False)

        return doc.SectionContents(initial_paragraphs,
                                   sub_sections)
