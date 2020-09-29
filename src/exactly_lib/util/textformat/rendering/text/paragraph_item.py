from typing import List, Iterable, Callable

from exactly_lib.util.textformat.rendering.text.lists import ListFormats, ListFormat, list_format_with_indent_str, \
    list_format_with_separations
from exactly_lib.util.textformat.rendering.text.table.column_max_width import CELL_AS_LINES
from exactly_lib.util.textformat.rendering.text.table.formatter import TableFormatter
from exactly_lib.util.textformat.rendering.text.text import TextFormatter
from exactly_lib.util.textformat.rendering.text.wrapper import Indent, Wrapper
from exactly_lib.util.textformat.structure.core import Text, ParagraphItem
from exactly_lib.util.textformat.structure.lists import HeaderContentList, HeaderContentListItem, Format
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.table import Table, TableCell
from exactly_lib.util.textformat.structure.utils import ParagraphItemVisitor


class Formatter:
    def __init__(self,
                 text_formatter: TextFormatter,
                 wrapper: Wrapper = Wrapper(),
                 num_item_separator_lines: int = 1,
                 list_formats: ListFormats = ListFormats(),
                 literal_layout_indent: str = '',
                 ):
        self.text_formatter = text_formatter
        self.list_formats = list_formats
        self.wrapper = wrapper
        self.num_item_separator_lines = num_item_separator_lines
        self.separator_lines = self.wrapper.blank_lines(num_item_separator_lines)
        self.text_item_formatter = _ParagraphItemFormatter(self)
        self.literal_layout_indent = literal_layout_indent

    def format_paragraph_items(self, items: List[ParagraphItem]) -> List[str]:
        ret_val = []
        for item in items:
            if ret_val:
                ret_val.extend(self.separator_lines)
            ret_val.extend(self.format_paragraph_item(item))
        return ret_val

    def format_paragraph_item(self, item: ParagraphItem) -> List[str]:
        return self.text_item_formatter.visit(item)

    def format_paragraph(self, paragraph: Paragraph) -> List[str]:
        ret_val = []
        for start_on_new_line_block in paragraph.start_on_new_line_blocks:
            assert isinstance(start_on_new_line_block, Text)
            ret_val.extend(self.format_text(start_on_new_line_block))
        return ret_val

    def format_text(self, text: Text) -> List[str]:
        return self.wrapper.wrap(self.text_formatter.apply(text))

    def format_str(self, s: str) -> List[str]:
        return self.wrapper.wrap(s)

    def format_literal_layout(self, literal_layout: LiteralLayout) -> List[str]:
        lines = literal_layout.literal_text.splitlines()
        with self.wrapper.indent_increase(Indent.identical(self.literal_layout_indent)):
            return self.wrapper.no_word_wrap(lines)

    def format_header_content_list(self, the_list: HeaderContentList) -> List[str]:
        list_format = self.resolve_list_format(the_list.list_format)
        return self.format_header_value_list_according_to_format(the_list.items,
                                                                 list_format)

    def format_header_value_list_according_to_format(self,
                                                     items: Iterable[HeaderContentListItem],
                                                     list_format: ListFormat) -> List[str]:
        return _ListFormatter(self, list_format, items).apply()

    def resolve_list_format(self, format_on_list: Format) -> ListFormat:
        list_format = self.list_formats.for_type(format_on_list.list_type)
        if format_on_list.custom_indent_spaces is not None:
            indent_str = format_on_list.custom_indent_spaces * ' '
            list_format = list_format_with_indent_str(list_format, indent_str)
        if format_on_list.custom_separations is not None:
            list_format = list_format_with_separations(list_format, format_on_list.custom_separations)
        return list_format

    def format_table(self, table: Table) -> List[str]:
        first_line_indent = self.wrapper.current_indent.first_line
        available_width = self.wrapper.page_width - len(first_line_indent)
        if available_width <= 0:
            return []
        formatter = TableFormatter(self._paragraph_items_formatter_for_given_width_for_table_formatter,
                                   available_width,
                                   table)
        un_indented_lines = formatter.apply()
        return [first_line_indent + line for line in un_indented_lines]

    def _paragraph_items_formatter_for_given_width_for_table_formatter(self, width: int,
                                                                       ) -> Callable[[TableCell], CELL_AS_LINES]:
        formatter = Formatter(self.text_formatter,
                              Wrapper(page_width=width),
                              num_item_separator_lines=self.num_item_separator_lines,
                              list_formats=self.list_formats)
        return lambda cell: formatter.format_paragraph_items(cell.paragraph_items)


class _ListFormatter:
    def __init__(self,
                 formatter: Formatter,
                 list_format: ListFormat,
                 items: Iterable[HeaderContentListItem],
                 ):
        self.formatter = formatter
        self.wrapper = formatter.wrapper
        self.list_format = list_format
        self.items_list = list(items)
        self.num_items = len(self.items_list)
        separations = list_format.separations
        self.blank_lines_between_elements = formatter.wrapper.blank_lines(
            separations.num_blank_lines_between_elements)
        self.blank_lines_between_header_and_content = formatter.wrapper.blank_lines(
            separations.num_blank_lines_between_header_and_contents)
        self.ret_val = []

    def apply(self) -> List[str]:
        ret_val = self.ret_val
        with self.wrapper.indent_increase(Indent.identical(self.list_format.indent_str)):
            for (item_number, item) in enumerate(self.items_list, start=1):
                if item_number > 1:
                    ret_val.extend(self.blank_lines_between_elements)
                self._format_header(item, item_number)
                self._format_content(item, item_number)
        return ret_val

    def _format_header(self, item: HeaderContentListItem, item_number: int):
        header_string = self.list_format.header_format.header_text(item_number,
                                                                   self.num_items,
                                                                   self.formatter.text_formatter,
                                                                   item.header)
        with self.wrapper.indent_increase(self.header_indent(item_number)):
            self.ret_val.extend(self.formatter.format_str(header_string))

    def _format_content(self, item: HeaderContentListItem, item_number: int):
        content_items_list = list(item.content_paragraph_items)
        if content_items_list:
            self.ret_val.extend(self.blank_lines_between_header_and_content)
            with self.wrapper.indent_increase(self.content_indent(item_number)):
                self.ret_val.extend(self.formatter.format_paragraph_items(content_items_list))

    def header_indent(self, item_number: int) -> Indent:
        following_lines_indent = self.list_format.header_format.following_header_lines_indent(item_number,
                                                                                              self.num_items)
        return Indent('', following_lines_indent)

    def content_indent(self, item_number: int) -> Indent:
        indent_str = self.list_format.header_format.contents_indent(self.num_items)
        return Indent(indent_str, indent_str)


class _ParagraphItemFormatter(ParagraphItemVisitor[List[str]]):
    def __init__(self, formatter: Formatter):
        self.formatter = formatter

    def visit_paragraph(self, paragraph: Paragraph) -> List[str]:
        return self.formatter.format_paragraph(paragraph)

    def visit_header_value_list(self, header_value_list: HeaderContentList) -> List[str]:
        return self.formatter.format_header_content_list(header_value_list)

    def visit_literal_layout(self, literal_layout: LiteralLayout) -> List[str]:
        return self.formatter.format_literal_layout(literal_layout)

    def visit_table(self, table: Table) -> List[str]:
        return self.formatter.format_table(table)
