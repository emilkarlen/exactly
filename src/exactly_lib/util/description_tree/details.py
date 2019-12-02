from typing import Sequence, Any

from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderer import DetailsRenderer, NodeRenderer
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib.util.strings import ToStringObject


class DetailsRendererOfConstant(DetailsRenderer):
    def __init__(self, detail: Detail):
        self._detail = detail

    def render(self) -> Sequence[Detail]:
        return [self._detail]


class String(DetailsRenderer):
    def __init__(self, to_string_object: ToStringObject):
        self._to_string_object = to_string_object

    def render(self) -> Sequence[Detail]:
        return [tree.StringDetail(self._to_string_object)]


class PreFormattedString(DetailsRenderer):
    def __init__(self,
                 to_string_object: ToStringObject,
                 string_is_line_ended: bool = False,
                 ):
        self._to_string_object = to_string_object
        self._string_is_line_ended = string_is_line_ended

    def render(self) -> Sequence[Detail]:
        return [tree.PreFormattedStringDetail(self._to_string_object,
                                              self._string_is_line_ended)]


class HeaderAndValue(DetailsRenderer):
    def __init__(self,
                 header: ToStringObject,
                 value: DetailsRenderer,
                 ):
        self._header = header
        self._value = value

    def render(self) -> Sequence[Detail]:
        return [
            tree.HeaderAndValueDetail(
                self._header,
                self._value.render(),
            )
        ]


class Tree(DetailsRenderer):
    def __init__(self, tree_: NodeRenderer[Any]):
        self._tree = tree_

    def render(self) -> Sequence[Detail]:
        return [tree.TreeDetail(self._tree.render())]
