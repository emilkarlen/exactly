from enum import Enum

from shellcheck_lib.general.textformat.structure.core import Text, ParagraphItem


class HeaderContentListItem(tuple):
    def __new__(cls,
                header: Text,
                content_paragraph_items: iter = ()):
        """
        :type content_paragraph_items: List[ParagraphItem]
        """
        return tuple.__new__(cls, (header, list(content_paragraph_items)))

    @property
    def header(self) -> Text:
        return self[0]

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


class HeaderContentList(ParagraphItem):
    def __init__(self,
                 list_type: ListType,
                 items: iter,
                 custom_indent_spaces: int = None):
        """
        :param custom_indent_spaces: Indentation of the list.
        Overrides settings defined by a formatter.
        :param items: [HeaderValueListItem]
        :return:
        """
        self.list_type = list_type
        self.items = items
        self.custom_indent_spaces = custom_indent_spaces
