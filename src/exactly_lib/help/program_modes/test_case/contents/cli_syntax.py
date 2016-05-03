from exactly_lib.help.utils.render import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class CliSyntaxRenderer(SectionContentsRenderer):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents([docs.para('TODO case cli syntax contents')],
                                   [])
