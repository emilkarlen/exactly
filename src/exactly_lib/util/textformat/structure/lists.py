from enum import Enum
from typing import Iterable, List

from exactly_lib.util.textformat.structure.core import Text, ParagraphItem


class HeaderContentListItem(tuple):
    def __new__(cls,
                header: Text,
                content_paragraph_items: Iterable[ParagraphItem] = ()):
        return tuple.__new__(cls, (header, list(content_paragraph_items)))

    @property
    def header(self) -> Text:
        return self[0]

    @property
    def content_paragraph_items(self) -> List[ParagraphItem]:
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
                 items: Iterable[HeaderContentListItem],
                 list_format: Format):
        self._items = items
        self._format = list_format

    @property
    def items(self) -> Iterable[HeaderContentListItem]:
        return self._items

    @property
    def list_format(self) -> Format:
        return self._format
