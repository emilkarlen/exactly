from shellcheck_lib.general.textformat.structure import core, paragraph, lists

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
