from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.lists import HeaderContentList
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.table import Table

T = TypeVar('T')


class ParagraphItemVisitor(Generic[T], ABC):
    def visit(self, item: ParagraphItem) -> T:
        if isinstance(item, Paragraph):
            return self.visit_paragraph(item)
        if isinstance(item, HeaderContentList):
            return self.visit_header_value_list(item)
        if isinstance(item, LiteralLayout):
            return self.visit_literal_layout(item)
        if isinstance(item, Table):
            return self.visit_table(item)
        raise TypeError('Unknown {}: {}'.format(ParagraphItem.__name__, str(type(item))))

    @abstractmethod
    def visit_paragraph(self, paragraph: Paragraph) -> T:
        pass

    @abstractmethod
    def visit_header_value_list(self, header_value_list: HeaderContentList) -> T:
        pass

    @abstractmethod
    def visit_literal_layout(self, x: LiteralLayout) -> T:
        pass

    @abstractmethod
    def visit_table(self, table: Table) -> T:
        pass
