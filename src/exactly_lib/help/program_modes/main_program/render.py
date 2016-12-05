from exactly_lib.help.program_modes.main_program.contents import MainCliSyntaxDocumentation
from exactly_lib.help.utils.cli_program_documentation_rendering import ProgramDocumentationSectionContentsRenderer
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.textformat.structure import document as doc


class OverviewRenderer(SectionContentsRenderer):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        renderer = ProgramDocumentationSectionContentsRenderer(MainCliSyntaxDocumentation())
        return renderer.apply(environment)
