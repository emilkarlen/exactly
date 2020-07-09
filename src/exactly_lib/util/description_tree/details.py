import itertools
from typing import Sequence, Any

from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderer import DetailsRenderer, NodeRenderer
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib.util.simple_textstruct.structure import TextStyle, TEXT_STYLE__NEUTRAL
from exactly_lib.util.str_.str_constructor import ToStringObject


class DetailsRendererOfConstant(DetailsRenderer):
    def __init__(self, details: Sequence[Detail]):
        self._details = details

    def render(self) -> Sequence[Detail]:
        return self._details


def empty() -> DetailsRenderer:
    return DetailsRendererOfConstant(())


class SequenceRenderer(DetailsRenderer):
    def __init__(self, details: Sequence[DetailsRenderer]):
        self._details = details

    def render(self) -> Sequence[Detail]:
        return list(
            itertools.chain.from_iterable([
                detail.render()
                for detail in self._details
            ])
        )


class IndentedRenderer(DetailsRenderer):
    def __init__(self, details: DetailsRenderer):
        self._details = details

    def render(self) -> Sequence[Detail]:
        return [
            tree.IndentedDetail(self._details.render())
        ]


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
                 header_text_style: TextStyle = TEXT_STYLE__NEUTRAL
                 ):
        self._header = header
        self._value = value
        self._header_text_style = header_text_style

    def render(self) -> Sequence[Detail]:
        return [
            tree.HeaderAndValueDetail(
                self._header,
                self._value.render(),
                self._header_text_style,
            )
        ]


class Tree(DetailsRenderer):
    def __init__(self, tree_: NodeRenderer[Any]):
        self._tree = tree_

    def render(self) -> Sequence[Detail]:
        return [tree.TreeDetail(self._tree.render())]
