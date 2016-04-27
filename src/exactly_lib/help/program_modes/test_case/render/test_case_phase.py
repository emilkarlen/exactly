from exactly_lib.help.program_modes.test_case.render.utils import TestCasePhaseRendererBase
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc


class TestCasePhaseOverviewRenderer(TestCasePhaseRendererBase):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return self.test_case_phase_documentation.render()
