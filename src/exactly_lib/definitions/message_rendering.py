from typing import List

from exactly_lib.util.textformat.rendering.text import section, paragraph_item
from exactly_lib.util.textformat.rendering.text import text
from exactly_lib.util.textformat.rendering.text.lists import list_formats_with
from exactly_lib.util.textformat.rendering.text.wrapper import Wrapper
from exactly_lib.util.textformat.structure import structures as docs, core


def render_single_text_cell_table_to_lines(str_or_text_cell_rows,
                                           indent: str = '') -> List[str]:
    return [indent + table_row
            for table_row in
            paragraph_formatter().format_table(docs.single_text_cell_table(str_or_text_cell_rows))
            ]


def render_paragraph_item(p: core.ParagraphItem) -> List[str]:
    return paragraph_formatter().format_paragraph_item(p)


def paragraph_formatter(page_width: int = 100) -> paragraph_item.Formatter:
    text_formatter = text.TextFormatter(_HelpCrossReferenceFormatter())
    return paragraph_item.Formatter(text_formatter,
                                    Wrapper(page_width=page_width),
                                    list_formats=list_formats_with(indent_str='  '))


def section_formatter(page_width) -> section.Formatter:
    return section.Formatter(paragraph_formatter(page_width),
                             section_content_indent_str='   ')


class _HelpCrossReferenceFormatter(text.CrossReferenceFormatter):
    def apply(self, cross_reference: core.CrossReferenceText) -> str:
        raise ValueError('error message rendering should not use cross references: ' + str(cross_reference))
