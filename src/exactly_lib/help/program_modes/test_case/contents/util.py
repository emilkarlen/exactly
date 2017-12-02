from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.util.textformat.building.section_contents_renderer import SectionContentsRenderer
from exactly_lib.util.textformat.textformat_parser import TextParser


class SectionContentsRendererWithSetup(SectionContentsRenderer):
    def __init__(self, setup: Setup,
                 format_map: dict):
        self.setup = setup
        self.text_parser = TextParser(format_map)

    def fnap(self, s: str, extra: dict = None) -> list:
        return self.text_parser.fnap(s, extra)
