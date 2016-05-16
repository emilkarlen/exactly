from exactly_lib.help.program_modes.main_program.contents import MainCliSyntaxDocumentation
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.cli_syntax.render.cli_program_syntax import ProgramDocumentationSectionContentsRenderer
from exactly_lib.util.textformat.structure import document as doc


class OverviewRenderer(SectionContentsRenderer):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        renderer = ProgramDocumentationSectionContentsRenderer(MainCliSyntaxDocumentation())
        return renderer.apply(environment)
