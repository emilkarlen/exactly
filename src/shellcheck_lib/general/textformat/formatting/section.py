from shellcheck_lib.general.textformat.formatting import paragraph_item
from shellcheck_lib.general.textformat.structure.document import SectionContents, Section


class Separation(tuple):
    def __new__(cls,
                between_sections: int = 1,
                between_header_and_content: int = 1,
                between_initial_paragraphs_and_sub_sections: int = 1):
        return tuple.__new__(cls, (between_sections,
                                   between_header_and_content,
                                   between_initial_paragraphs_and_sub_sections))

    @property
    def value(self) -> str:
        return self[0]


def no_separation() -> Separation:
    return Separation(0, 0, 0)


class Formatter:
    def __init__(self,
                 paragraph_item_formatter: paragraph_item.Formatter,
                 separation: Separation = Separation()):
        self.paragraph_item_formatter = paragraph_item_formatter
        self.separation = separation

    def format_section_contents(self, section_contents: SectionContents) -> list:
        ret_val = []
        ret_val.extend(self.paragraph_item_formatter.format_paragraph_items(section_contents.initial_paragraphs))
        ret_val.extend(self.format_sections(section_contents.sections))
        return ret_val

    def format_section(self, section: Section) -> list:
        ret_val = []
        ret_val.extend(self.paragraph_item_formatter.format_text(section.header))
        ret_val.extend(self.format_section_contents(section.contents))
        return ret_val

    def format_sections(self, sections: list) -> list:
        ret_val = []
        for section in sections:
            ret_val.extend(self.format_section(section))
        return ret_val
