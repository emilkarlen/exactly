from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.help.utils.rendering.section_contents_renderer import SectionContentsRenderer


class SectionContentsRendererWithSetup(SectionContentsRenderer):
    def __init__(self, setup: Setup):
        self.setup = setup
