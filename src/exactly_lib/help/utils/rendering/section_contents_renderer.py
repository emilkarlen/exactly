from exactly_lib.help.utils.rendering.cross_reference import CrossReferenceTextConstructor
from exactly_lib.util.textformat.structure import document as doc


class RenderingEnvironment(tuple):
    def __new__(cls,
                cross_ref_text_constructor: CrossReferenceTextConstructor,
                render_simple_header_value_lists_as_tables: bool = False):
        return tuple.__new__(cls, (cross_ref_text_constructor,
                                   render_simple_header_value_lists_as_tables))

    @property
    def cross_ref_text_constructor(self) -> CrossReferenceTextConstructor:
        return self[0]

    @property
    def render_simple_header_value_lists_as_tables(self) -> bool:
        return self[1]


class SectionContentsRenderer:
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        raise NotImplementedError()


class SectionRenderer:
    def apply(self, environment: RenderingEnvironment) -> doc.Section:
        raise NotImplementedError()


class SectionContentsRendererForConstantContents(SectionContentsRenderer):
    def __init__(self, section_contents: doc.SectionContents):
        self.section_contents = section_contents

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return self.section_contents
