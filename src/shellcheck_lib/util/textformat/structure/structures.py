from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import Text, ParagraphItem
from shellcheck_lib.util.textformat.structure.literal_layout import LiteralLayout
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph

SEPARATION_OF_HEADER_AND_CONTENTS = lists.Separations(1, 1)


def simple_header_only_list(string_headers: iter,
                            list_type: lists.ListType) -> lists.HeaderContentList:
    items = [header_only_item(header) for header in string_headers]
    return lists.HeaderContentList(items,
                                   lists.Format(list_type))


def simple_list(items: iter,
                list_type: lists.ListType) -> lists.HeaderContentList:
    return lists.HeaderContentList(items,
                                   lists.Format(list_type))


def simple_list_with_space_between_elements_and_content(items: iter,
                                                        list_type: lists.ListType) -> lists.HeaderContentList:
    return lists.HeaderContentList(items,
                                   lists.Format(list_type,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))


def list_item(header: str,
              content: list) -> lists.HeaderContentListItem:
    return lists.HeaderContentListItem(Text(header),
                                       content)


def header_only_item(header: str) -> lists.HeaderContentListItem:
    return list_item(header, [])


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
