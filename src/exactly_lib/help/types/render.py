from exactly_lib.help.types.contents_structure import TypeDocumentation
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts.test_case.phase_names import ACT_PHASE_NAME
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class IndividualTypeRenderer(SectionContentsRenderer):
    def __init__(self, type_: TypeDocumentation):
        self.type = type_
        self.rendering_environment = None
        format_map = {
            # 'type_concept': formatting.concept(TYPE_CONCEPT_INFO.name().singular),
            'act_phase': ACT_PHASE_NAME.emphasis,
        }
        self._parser = TextParser(format_map)

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        self.rendering_environment = environment
        initial_paragraphs = [docs.para(self.type.single_line_description())]
        # initial_paragraphs.extend(self._default_reporter_info())
        # initial_paragraphs.extend(self.type.main_description_rest())
        sub_sections = []
        # append_sections_if_contents_is_non_empty(
        #     sub_sections,
        #     [(self._parser.format('{act_phase} phase contents'), self.type.act_phase_contents()),
        #      (self._parser.format('Syntax of {act_phase} phase contents'), self.type.act_phase_contents_syntax())])
        # sub_sections.extend(see_also_sections(self.type.see_also_items(), environment))
        return doc.SectionContents(initial_paragraphs, sub_sections)
