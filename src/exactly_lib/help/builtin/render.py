from exactly_lib.help.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class IndividualBuiltinSymbolRenderer(SectionContentsRenderer):
    def __init__(self, builtin_doc: BuiltinSymbolDocumentation):
        self.builtin_doc = builtin_doc
        format_map = {
            # 'type_concept': formatting.concept(TYPE_CONCEPT_INFO.name().singular),
        }
        self._parser = TextParser(format_map)

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        initial_paragraphs = [docs.para(self.builtin_doc.single_line_description())]
        initial_paragraphs.extend(self.builtin_doc.description.initial_paragraphs)
        return doc.SectionContents(initial_paragraphs, self.builtin_doc.description.sections)
