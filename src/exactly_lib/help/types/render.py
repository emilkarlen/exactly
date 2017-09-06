from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.types.contents_structure import TypeDocumentation
from exactly_lib.help.utils.doc_utils import synopsis_section
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts.test_case.phase_names import ACT_PHASE_NAME
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class IndividualTypeRenderer(SectionContentsRenderer):
    def __init__(self, type_doc: TypeDocumentation):
        self.doc = type_doc
        self.rendering_environment = None
        format_map = {
            # 'type_concept': formatting.concept(TYPE_CONCEPT_INFO.name().singular),
            'act_phase': ACT_PHASE_NAME.emphasis,
        }
        self._parser = TextParser(format_map)

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        self.rendering_environment = environment
        initial_paragraphs = [docs.para(self.doc.single_line_description())]
        sub_sections = []

        if self.doc.invokation_variants():
            sub_sections.append(synopsis_section(
                invokation_variants_content(None,
                                            self.doc.invokation_variants(),
                                            [])))

        return doc.SectionContents(initial_paragraphs, sub_sections)
