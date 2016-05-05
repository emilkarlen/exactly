from exactly_lib.help.program_modes.main_program.contents import test_case_overview_help
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc


class OverviewRenderer(SectionContentsRenderer):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents(test_case_overview_help(), [])
