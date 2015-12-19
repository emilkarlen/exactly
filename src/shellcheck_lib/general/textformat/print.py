from textwrap import TextWrapper

from shellcheck_lib.general.textformat.structure import Paragraph, ParagraphItem, ParagraphItemVisitor


class Formatter:
    def __init__(self,
                 page_width: int = 70,
                 num_item_separator_lines: int = 1):
        self.page_width = page_width
        self.text_item_formatter = _ParagraphItemFormatter(self)
        self.text_wrapper = TextWrapper(width=page_width)
        self.separator_lines = num_item_separator_lines * ['']

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
            ret_val.extend(self.text_wrapper.wrap(start_on_new_line_block))
        return ret_val


class _ParagraphItemFormatter(ParagraphItemVisitor):
    def __init__(self, printer: Formatter):
        self.printer = printer

    def visit_paragraph(self, paragraph: Paragraph):
        return self.printer.format_paragraph(paragraph)
