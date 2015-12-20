from textwrap import TextWrapper

from shellcheck_lib.general.textformat.formatting.lists import ListFormats, ListFormat
from shellcheck_lib.general.textformat.formatting.wrapper import Indent
from shellcheck_lib.general.textformat.structure.core import Text, ParagraphItem
from shellcheck_lib.general.textformat.structure.lists import HeaderValueList, HeaderValueListItem
from shellcheck_lib.general.textformat.structure.paragraph import Paragraph
from shellcheck_lib.general.textformat.structure.utils import ParagraphItemVisitor


class Formatter:
    def __init__(self,
                 page_width: int = 70,
                 num_item_separator_lines: int = 1,
                 list_formats: ListFormats = ListFormats()):
        self.list_formats = list_formats
        self.text_wrapper = TextWrapper(width=page_width)
        self.separator_lines = num_item_separator_lines * ['']
        self.text_item_formatter = _ParagraphItemFormatter(self)
        self._saved_indents_stack = []

    @property
    def page_width(self) -> int:
        return self.text_wrapper.width

    @property
    def current_indent(self) -> Indent:
        return Indent(self.text_wrapper.initial_indent,
                      self.text_wrapper.subsequent_indent)

    @property
    def saved_indents_stack(self) -> list:
        return self._saved_indents_stack

    def push_indent(self, indent: Indent):
        text_wrapper = self.text_wrapper
        self._saved_indents_stack.insert(0, self.current_indent)
        text_wrapper.initial_indent = indent.first_line
        text_wrapper.subsequent_indent = indent.following_lines

    def push_indent_increase(self, delta: Indent):
        text_wrapper = self.text_wrapper
        indent = Indent(text_wrapper.initial_indent + delta.first_line,
                        text_wrapper.subsequent_indent + delta.following_lines)
        self.push_indent(indent)

    def pop_indent(self):
        indent = self._saved_indents_stack.pop()
        self.text_wrapper.initial_indent = indent.first_line
        self.text_wrapper.subsequent_indent = indent.following_lines

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
        return self.text_wrapper.wrap(text.value)

    def format_header_value_list(self, the_list: HeaderValueList) -> list:
        list_format = self.list_formats.for_type(the_list.list_type)
        return self.format_header_value_list_according_to_format(the_list.items,
                                                                 list_format)

    def format_header_value_list_according_to_format(self,
                                                     items: iter,
                                                     list_format: ListFormat) -> list:
        """
        :type items: [HeaderValueListItem]
        """
        return _ListFormatter(self, list_format, items).apply()


class _ListFormatter:
    def __init__(self,
                 formatter: Formatter,
                 list_format: ListFormat,
                 items: iter):
        self.formatter = formatter
        self.list_format = list_format
        self.items_list = list(items)
        self.num_items = len(self.items_list)
        separations = list_format.separations
        self.blank_lines_between_elements = separations.num_blank_lines_between_elements * ['']
        self.blank_lines_between_header_and_content = separations.num_blank_lines_between_header_and_value * ['']
        self.ret_val = []

    def apply(self) -> list:
        ret_val = self.ret_val
        for (item_number, item) in enumerate(self.items_list, start=1):
            assert isinstance(item, HeaderValueListItem), ('The list item is not a %s' % str(HeaderValueListItem))
            if item_number > 1:
                ret_val.extend(self.blank_lines_between_elements)
            self._format_header(item, item_number)
            self._format_content(item, item_number)
        return ret_val

    def _format_header(self, item, item_number):
        self.push_header_indent(item_number)
        header_text = self.list_format.header_format.header_text(item_number,
                                                                 self.num_items,
                                                                 item.header)
        self.ret_val.extend(self.formatter.format_text(header_text))
        self.formatter.pop_indent()

    def _format_content(self, item, item_number):
        content_items_list = list(item.value_paragraph_items)
        if content_items_list:
            self.ret_val.extend(self.blank_lines_between_header_and_content)
            self.push_content_indent(item_number)
            self.ret_val.extend(self.formatter.format_paragraph_items(content_items_list))
            self.formatter.pop_indent()

    def push_header_indent(self, item_number):
        following_lines_indent = self.list_format.header_format.following_header_lines_indent(item_number,
                                                                                              self.num_items)
        indent_delta = Indent('', following_lines_indent)
        self.formatter.push_indent_increase(indent_delta)

    def push_content_indent(self, item_number):
        indent_str = self.list_format.header_format.value_indent(self.num_items)
        indent_delta = Indent(indent_str, indent_str)
        self.formatter.push_indent_increase(indent_delta)


class _ParagraphItemFormatter(ParagraphItemVisitor):
    def __init__(self, formatter: Formatter):
        self.formatter = formatter

    def visit_paragraph(self, paragraph: Paragraph):
        return self.formatter.format_paragraph(paragraph)

    def visit_header_value_list(self, header_value_list: HeaderValueList):
        return self.formatter.format_header_value_list(header_value_list)
