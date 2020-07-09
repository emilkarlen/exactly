from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic, Any, Optional

from exactly_lib.util.simple_textstruct.structure import TextStyle, TEXT_STYLE__NEUTRAL
from exactly_lib.util.str_.str_constructor import ToStringObject

RET = TypeVar('RET')


class Detail(ABC):
    @abstractmethod
    def accept(self, visitor: 'DetailVisitor[RET]') -> RET:
        pass


NODE_DATA = TypeVar('NODE_DATA')


class Node(Generic[NODE_DATA]):
    def __init__(self,
                 header: str,
                 data: NODE_DATA,
                 details: Sequence[Detail],
                 children: Sequence['Node[NODE_DATA]']):
        self._header = header
        self._data = data
        self._details = details
        self._children = children

    @staticmethod
    def empty(header: str, data: NODE_DATA) -> 'Node[NODE_DATA]':
        """Gives a node without details and children"""
        return Node(header, data, (), ())

    @staticmethod
    def leaf(header: str, data: NODE_DATA, details: Sequence[Detail]) -> 'Node[NODE_DATA]':
        """Gives a node without children"""
        return Node(header, data, details, ())

    @property
    def header(self) -> str:
        return self._header

    @property
    def data(self) -> NODE_DATA:
        return self._data

    @property
    def details(self) -> Sequence[Detail]:
        return self._details

    @property
    def children(self) -> Sequence['Node[NODE_DATA]']:
        return self._children


class StringDetail(Detail):
    """A detail that is a string without any special structure."""

    def __init__(self, to_string_object: ToStringObject):
        self._to_string_object = to_string_object

    def accept(self, visitor: 'DetailVisitor[RET]') -> RET:
        return visitor.visit_string(self)

    @property
    def string(self) -> ToStringObject:
        return self._to_string_object


class PreFormattedStringDetail(Detail):
    def __init__(self,
                 to_string_object: ToStringObject,
                 string_is_line_ended: bool = False
                 ):
        self._to_string_object = to_string_object
        self._string_is_line_ended = string_is_line_ended

    def accept(self, visitor: 'DetailVisitor[RET]') -> RET:
        return visitor.visit_pre_formatted_string(self)

    @property
    def object_with_to_string(self) -> ToStringObject:
        return self._to_string_object

    @property
    def string_is_line_ended(self) -> bool:
        return self._string_is_line_ended


class HeaderAndValueDetail(Detail):
    def __init__(self,
                 header: ToStringObject,
                 values: Sequence[Detail],
                 header_text_style: TextStyle = TEXT_STYLE__NEUTRAL,
                 ):
        self._header = header
        self._values = values
        self._header_text_style = header_text_style

    def accept(self, visitor: 'DetailVisitor[RET]') -> RET:
        return visitor.visit_header_and_value(self)

    @property
    def header(self) -> ToStringObject:
        return self._header

    @property
    def values(self) -> Sequence[Detail]:
        return self._values

    @property
    def header_text_style(self) -> Optional[TextStyle]:
        return self._header_text_style


class IndentedDetail(Detail):
    def __init__(self, details: Sequence[Detail]):
        self._details = details

    def accept(self, visitor: 'DetailVisitor[RET]') -> RET:
        return visitor.visit_indented(self)

    @property
    def details(self) -> Sequence[Detail]:
        return self._details


class TreeDetail(Detail):
    """Makes a Detail of a Node."""

    def __init__(self,
                 tree: Node[Any],
                 header_text_style: TextStyle = TEXT_STYLE__NEUTRAL,
                 ):
        self._tree = tree
        self._header_text_style = header_text_style

    @property
    def tree(self) -> Node[Any]:
        return self._tree

    @property
    def header_text_style(self) -> TextStyle:
        return self._header_text_style

    def accept(self, visitor: 'DetailVisitor[RET]') -> RET:
        return visitor.visit_tree(self)


class DetailVisitor(Generic[RET], ABC):
    @abstractmethod
    def visit_string(self, x: StringDetail) -> RET:
        pass

    @abstractmethod
    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> RET:
        pass

    @abstractmethod
    def visit_header_and_value(self, x: HeaderAndValueDetail) -> RET:
        pass

    @abstractmethod
    def visit_indented(self, x: IndentedDetail) -> RET:
        pass

    @abstractmethod
    def visit_tree(self, x: TreeDetail) -> RET:
        pass
