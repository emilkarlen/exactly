from shellcheck_lib.util.textformat.structure.core import Text, ParagraphItem
from shellcheck_lib.util.textformat.structure.lists import ListType, HeaderContentList, Format, HeaderContentListItem
from shellcheck_lib.util.textformat.structure.literal_layout import LiteralLayout
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph


def simple_header_only_list(string_headers: iter,
                            list_type: ListType) -> HeaderContentList:
    items = [header_only_item(header) for header in string_headers]
    return HeaderContentList(items,
                             Format(list_type))


def item(header: str,
         content: list) -> HeaderContentListItem:
    return HeaderContentListItem(Text(header),
                                 content)


def header_only_item(header: str) -> HeaderContentListItem:
    return item(header, [])


def para(str_or_text) -> ParagraphItem:
    if isinstance(str_or_text, str):
        text_ = Text(str_or_text)
    else:
        text_ = str_or_text
    return Paragraph([text_])


def text(s: str) -> Text:
    return Text(s)


def literal_layout(s: str) -> ParagraphItem:
    return LiteralLayout(s)
