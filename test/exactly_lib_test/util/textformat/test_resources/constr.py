from exactly_lib.util.textformat.formatting.text import paragraph_item as sut
from exactly_lib.util.textformat.formatting.text.text import CrossReferenceFormatter, TextFormatter
from exactly_lib.util.textformat.structure import core, paragraph, lists, table

BLANK_LINE = ''


def text(string: str) -> core.Text:
    return core.StringText(string)


def para(texts: iter) -> paragraph.Paragraph:
    return paragraph.Paragraph(texts)


def single_text_para(string: str) -> paragraph.Paragraph:
    return paragraph.Paragraph([text(string)])


def single_text_cell(string: str) -> table.TableCell:
    return table.single_paragraph_cell(paragraph.Paragraph([text(string)]))


def item(header: str,
         content: list) -> lists.HeaderContentListItem:
    return lists.HeaderContentListItem(text(header),
                                       content)


def header_only_item(header: str) -> lists.HeaderContentListItem:
    return item(header, [])


class TitleOnlyCrossReferenceFormatter(CrossReferenceFormatter):
    def apply(self, cross_reference: core.CrossReferenceText) -> str:
        return cross_reference.title


def formatter_with_page_width(page_width: int) -> sut.Formatter:
    return sut.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                         sut.Wrapper(page_width=page_width))


CROSS_REF_TITLE_ONLY_TEXT_FORMATTER = TextFormatter(TitleOnlyCrossReferenceFormatter())
