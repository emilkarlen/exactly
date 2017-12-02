from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor
from exactly_lib.util.textformat.textformat_parser import TextParser


class SectionContentsConstructorWithSetup(SectionContentsConstructor):
    def __init__(self, setup: Setup,
                 format_map: dict):
        self.setup = setup
        self.text_parser = TextParser(format_map)

    def fnap(self, s: str, extra: dict = None) -> list:
        return self.text_parser.fnap(s, extra)
