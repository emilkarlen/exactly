from enum import Enum

from exactly_lib.util.textformat.structure.core import TaggedItem, Text, ParagraphItem


class HeaderItem(TaggedItem):
    def __init__(self,
                 header: Text,
                 tags: set = None):
        self._header = header
        self._tags = set() if tags is None else tags

    @property
    def text(self) -> Text:
        return self._header

    @property
    def tags(self) -> set:
        return self._tags


class HeaderContentListItem(tuple):
    def __new__(cls,
                header: HeaderItem,
                content_paragraph_items: iter = ()):
        """
        :type content_paragraph_items: List[ParagraphItem]
        """
        return tuple.__new__(cls, (header, list(content_paragraph_items)))

    @property
    def header_item(self) -> HeaderItem:
        return self[0]

    @property
    def header(self) -> Text:
        return self.header_item.text

    @property
    def content_paragraph_items(self) -> iter:
        """
        :type: List[ParagraphItem]
        """
        return self[1]


class ListType(Enum):
    ITEMIZED_LIST = 1
    ORDERED_LIST = 2
    VARIABLE_LIST = 3


class Separations(tuple):
    def __new__(cls,
                num_blank_lines_between_elements: int,
                num_blank_lines_between_header_and_contents: int):
        return tuple.__new__(cls, (num_blank_lines_between_elements,
                                   num_blank_lines_between_header_and_contents))

    @property
    def num_blank_lines_between_elements(self) -> int:
        return self[0]

    @property
    def num_blank_lines_between_header_and_contents(self) -> int:
        return self[1]


class Format(tuple):
    def __new__(cls,
                list_type: ListType,
                custom_indent_spaces: int = None,
                custom_separations: Separations = None):
        """
        :param custom_indent_spaces: Indentation of the list.
        Overrides settings defined by a formatter.
        """
        return tuple.__new__(cls, (list_type,
                                   custom_indent_spaces,
                                   custom_separations))

    @property
    def list_type(self) -> ListType:
        return self[0]

    @property
    def custom_indent_spaces(self) -> int:
        return self[1]

    @property
    def custom_separations(self) -> Separations:
        return self[2]


class HeaderContentList(ParagraphItem):
    def __init__(self,
                 items: iter,
                 list_format: Format):
        """
        :param items: [`HeaderContentListItem`]
        """
        self._items = items
        self._format = list_format

    @property
    def items(self) -> iter:
        """
        :rtype: [`HeaderContentListItem`]
        """
        return self._items

    @property
    def list_format(self) -> Format:
        return self._format
