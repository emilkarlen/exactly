from textwrap import TextWrapper

from shellcheck_lib.general.textformat.formatting.lists import ListFormats
from shellcheck_lib.general.textformat.structure.core import Text, ParagraphItem
from shellcheck_lib.general.textformat.structure.lists import HeaderValueList
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
            ret_val.extend(self.text_wrapper.wrap(start_on_new_line_block.value))
        return ret_val

    def format_header_value_list(self, header_value_list: HeaderValueList):
        raise NotImplemented()


class _ParagraphItemFormatter(ParagraphItemVisitor):
    def __init__(self, printer: Formatter):
        self.printer = printer

    def visit_paragraph(self, paragraph: Paragraph):
        return self.printer.format_paragraph(paragraph)

    def visit_header_value_list(self, header_value_list: HeaderValueList):
        return self.printer.format_header_value_list(header_value_list)
