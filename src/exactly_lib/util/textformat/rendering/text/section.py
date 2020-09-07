from typing import List

from exactly_lib.util.textformat.rendering.text import paragraph_item
from exactly_lib.util.textformat.rendering.text.wrapper import Indent
from exactly_lib.util.textformat.structure.document import SectionContents, Section, SectionItem, SectionItemVisitor, \
    Article


class Separation(tuple):
    def __new__(cls,
                between_sections: int = 1,
                between_header_and_content: int = 1,
                between_initial_paragraphs_and_sub_sections: int = 1):
        return tuple.__new__(cls, (between_sections,
                                   between_header_and_content,
                                   between_initial_paragraphs_and_sub_sections))

    @property
    def between_sections(self) -> int:
        return self[0]

    @property
    def between_header_and_content(self) -> int:
        return self[1]

    @property
    def between_initial_paragraphs_and_sub_sections(self) -> int:
        return self[2]


def no_separation() -> Separation:
    return Separation(0, 0, 0)


class Formatter(SectionItemVisitor[List[str]]):
    def __init__(self,
                 paragraph_item_formatter: paragraph_item.Formatter,
                 separation: Separation = Separation(),
                 section_content_indent_str: str = '',
                 ):
        self.paragraph_item_formatter = paragraph_item_formatter
        self.section_content_indent = Indent(section_content_indent_str,
                                             section_content_indent_str)
        self.separation = separation
        self.wrapper = paragraph_item_formatter.wrapper

    def format_section_contents(self,
                                section_contents: SectionContents,
                                prepend_separator_for_contents: bool = False,
                                ) -> List[str]:
        ret_val = []
        init_para_lines = self.paragraph_item_formatter.format_paragraph_items(section_contents.initial_paragraphs)
        sections_lines = self.format_section_items(section_contents.sections)
        if prepend_separator_for_contents:
            if init_para_lines or sections_lines:
                ret_val.extend(self._blanks(self.separation.between_header_and_content))
        ret_val.extend(init_para_lines)
        if init_para_lines and sections_lines:
            ret_val.extend(self._blanks(self.separation.between_initial_paragraphs_and_sub_sections))
        ret_val.extend(sections_lines)
        return ret_val

    def format_section_item(self, section_item: SectionItem) -> List[str]:
        return section_item.accept(self)

    def format_section(self, section: Section) -> List[str]:
        ret_val = []
        ret_val.extend(self.paragraph_item_formatter.format_text(section.header))
        self.wrapper.push_indent_increase(self.section_content_indent)
        ret_val.extend(self.format_section_contents(section.contents, True))
        self.wrapper.pop_indent()
        return ret_val

    def format_section_items(self, section_items: list) -> List[str]:
        ret_val = []
        for section in section_items:
            if ret_val:
                ret_val.extend(self._blanks(self.separation.between_sections))
            ret_val.extend(self.format_section_item(section))
        return ret_val

    def visit_section(self, section: Section):
        return self.format_section(section)

    def visit_article(self, article: Article) -> List[str]:
        as_section = Section(article.header,
                             article.contents.combined_as_section_contents)

        return self.format_section(as_section)

    def _blanks(self, num_lines: int) -> List[str]:
        return self.wrapper.blank_lines(num_lines)
