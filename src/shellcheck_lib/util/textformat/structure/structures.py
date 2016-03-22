from shellcheck_lib.util.textformat.structure.core import Text
from shellcheck_lib.util.textformat.structure.lists import ListType, HeaderContentList, Format, HeaderContentListItem


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
