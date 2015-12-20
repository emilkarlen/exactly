from shellcheck_lib.general.textformat.structure.document import SectionContents, Section


class Formatter:
    def __init__(self,
                 page_width: int = 70):
        pass

    def format_sections(self, sections: list) -> list:
        raise NotImplementedError()

    def format_section(self, section_contents: Section) -> list:
        raise NotImplementedError()

    def format_section_contents(self, section_contents: SectionContents) -> list:
        return ['paragraph']
