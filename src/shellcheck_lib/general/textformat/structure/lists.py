from enum import Enum

from shellcheck_lib.general.textformat.structure.core import Text, ParagraphItem


class HeaderValueListItem(tuple):
    def __new__(cls,
                header: Text,
                value_paragraph_items: iter = ()):
        return tuple.__new__(cls, (header, value_paragraph_items))

    @property
    def header(self) -> Text:
        return self[0]

    @property
    def value_paragraph_items(self) -> iter:
        return self[1]


class ListType(Enum):
    ITEMIZED_LIST = 1
    ORDERED_LIST = 2
    VARIABLE_LIST = 3


class HeaderValueList(ParagraphItem):
    def __init__(self,
                 list_type: ListType,
                 items: iter):
        """
        :param items: [HeaderValueListItem]
        :return:
        """
        self.list_type = list_type
        self.items = items
