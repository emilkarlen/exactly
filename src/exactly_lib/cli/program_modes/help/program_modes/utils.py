from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import text, Text


def with_or_without_name(do_include_name: bool,
                         name: str,
                         contents_renderer: SectionContentsRenderer) -> SectionContentsRenderer:
    if do_include_name:
        return _WithElementNameRenderer(text(name), contents_renderer)
    else:
        return contents_renderer


class _WithElementNameRenderer(SectionContentsRenderer):
    def __init__(self,
                 header: Text,
                 contents_render: SectionContentsRenderer):
        self.header = header
        self.contents_render = contents_render

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents([],
                                   [doc.Section(self.header,
                                                self.contents_render.apply(environment))])
