from shellcheck_lib.util.textformat.formatting import paragraph_item as sut
from shellcheck_lib.util.textformat.structure import core, paragraph, lists

BLANK_LINE = ''


def text(string: str) -> core.Text:
    return core.Text(string)


def para(texts: iter) -> paragraph.Paragraph:
    return paragraph.Paragraph(texts)


def single_text_para(string: str) -> paragraph.Paragraph:
    return paragraph.Paragraph([text(string)])


def item(header: str,
         content: list) -> lists.HeaderContentListItem:
    return lists.HeaderContentListItem(text(header),
                                       content)


def header_only_item(header: str) -> lists.HeaderContentListItem:
    return item(header, [])


def formatter_with_page_width(page_width: int) -> sut.Formatter:
    return sut.Formatter(sut.Wrapper(page_width=page_width))
