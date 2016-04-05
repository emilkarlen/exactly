from shellcheck_lib.help.program_modes.test_case.render.utils import TestCasePhaseRendererBase
from shellcheck_lib.help.utils.render import RenderingEnvironment
from shellcheck_lib.util.textformat.structure import document as doc


class TestCasePhaseOverviewRenderer(TestCasePhaseRendererBase):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return self.test_case_phase_documentation.render()
