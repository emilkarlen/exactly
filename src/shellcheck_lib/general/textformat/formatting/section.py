from shellcheck_lib.general.textformat.formatting import paragraph_item
from shellcheck_lib.general.textformat.structure.document import SectionContents, Section


class Formatter:
    def __init__(self,
                 paragraph_item_formatter: paragraph_item.Formatter):
        self.paragraph_item_formatter = paragraph_item_formatter

    def format_sections(self, sections: list) -> list:
        raise NotImplementedError()

    def format_section(self, section_contents: Section) -> list:
        raise NotImplementedError()

    def format_section_contents(self, section_contents: SectionContents) -> list:
        ret_val = []
        ret_val.extend(self.paragraph_item_formatter.format_paragraph_items(section_contents.initial_paragraphs))
        return ret_val
