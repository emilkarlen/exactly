from shellcheck_lib.util.textformat.formatting.lists import ListFormats, ListFormat, list_format_with_indent_str, \
    list_format_with_separations
from shellcheck_lib.util.textformat.formatting.wrapper import Indent, Wrapper, identical_indent
from shellcheck_lib.util.textformat.structure.core import Text, ParagraphItem
from shellcheck_lib.util.textformat.structure.lists import HeaderContentList, HeaderContentListItem, Format
from shellcheck_lib.util.textformat.structure.literal_layout import LiteralLayout
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph
from shellcheck_lib.util.textformat.structure.utils import ParagraphItemVisitor


class Formatter:
    def __init__(self,
                 wrapper: Wrapper = Wrapper(),
                 num_item_separator_lines: int = 1,
                 list_formats: ListFormats = ListFormats()):
        self.list_formats = list_formats
        self.wrapper = wrapper
        self.separator_lines = self.wrapper.blank_lines(num_item_separator_lines)
        self.text_item_formatter = _ParagraphItemFormatter(self)

    def format_paragraph_items(self, items: iter) -> list:
        ret_val = []
        for item in items:
            if ret_val:
                ret_val.extend(self.separator_lines)
            ret_val.extend(self.format_paragraph_item(item))
        return ret_val

    def format_paragraph_item(self, item: ParagraphItem) -> list:
        return self.text_item_formatter.visit(item)

    def format_paragraph(self, paragraph: Paragraph) -> list:
        ret_val = []
        for start_on_new_line_block in paragraph.start_on_new_line_blocks:
            assert isinstance(start_on_new_line_block, Text)
            ret_val.extend(self.format_text(start_on_new_line_block))
        return ret_val

    def format_text(self, text: Text) -> list:
        return self.wrapper.wrap(text.value)

    def format_literal_layout(self, literal_layout: LiteralLayout) -> list:
        return []

    def format_header_content_list(self, the_list: HeaderContentList) -> list:
        list_format = self.resolve_list_format(the_list.list_format)
        return self.format_header_value_list_according_to_format(the_list.items,
                                                                 list_format)

    def format_header_value_list_according_to_format(self,
                                                     items: iter,
                                                     list_format: ListFormat) -> list:
        """
        :type items: [HeaderValueListItem]
        """
        return _ListFormatter(self, list_format, items).apply()

    def resolve_list_format(self, format_on_list: Format) -> ListFormat:
        list_format = self.list_formats.for_type(format_on_list.list_type)
        if format_on_list.custom_indent_spaces is not None:
            indent_str = format_on_list.custom_indent_spaces * ' '
            list_format = list_format_with_indent_str(list_format, indent_str)
        if format_on_list.custom_separations is not None:
            list_format = list_format_with_separations(list_format, format_on_list.custom_separations)
        return list_format


class _ListFormatter:
    def __init__(self,
                 formatter: Formatter,
                 list_format: ListFormat,
                 items: iter):
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

    def apply(self) -> list:
        ret_val = self.ret_val
        with self.wrapper.indent_increase(identical_indent(self.list_format.indent_str)):
            for (item_number, item) in enumerate(self.items_list, start=1):
                assert isinstance(item, HeaderContentListItem), (
                    'The list item is not a %s' % str(HeaderContentListItem))
                if item_number > 1:
                    ret_val.extend(self.blank_lines_between_elements)
                self._format_header(item, item_number)
                self._format_content(item, item_number)
        return ret_val

    def _format_header(self, item, item_number):
        header_text = self.list_format.header_format.header_text(item_number,
                                                                 self.num_items,
                                                                 item.header)
        with self.wrapper.indent_increase(self.header_indent(item_number)):
            self.ret_val.extend(self.formatter.format_text(header_text))

    def _format_content(self, item, item_number):
        content_items_list = list(item.content_paragraph_items)
        if content_items_list:
            self.ret_val.extend(self.blank_lines_between_header_and_content)
            with self.wrapper.indent_increase(self.content_indent(item_number)):
                self.ret_val.extend(self.formatter.format_paragraph_items(content_items_list))

    def header_indent(self, item_number) -> Indent:
        following_lines_indent = self.list_format.header_format.following_header_lines_indent(item_number,
                                                                                              self.num_items)
        return Indent('', following_lines_indent)

    def content_indent(self, item_number) -> Indent:
        indent_str = self.list_format.header_format.contents_indent(self.num_items)
        return Indent(indent_str, indent_str)


class _ParagraphItemFormatter(ParagraphItemVisitor):
    def __init__(self, formatter: Formatter):
        self.formatter = formatter

    def visit_paragraph(self, paragraph: Paragraph):
        return self.formatter.format_paragraph(paragraph)

    def visit_header_value_list(self, header_value_list: HeaderContentList):
        return self.formatter.format_header_content_list(header_value_list)
