from typing import Sequence, Generic, TypeVar

from exactly_lib.common.report_rendering.components import SequenceRenderer, \
    ELEMENT, Renderer
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.structure import MinorBlock, ElementProperties, \
    LineElement

T = TypeVar('T')


class ConstantR(Generic[T], Renderer[T]):
    def __init__(self, element: T):
        self._element = element

    def render(self) -> T:
        return self._element


class ConcatenationR(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    def __init__(self, elements: Sequence[Renderer[Sequence[ELEMENT]]]):
        self._elements = elements

    def render(self) -> Sequence[ELEMENT]:
        ret_val = []
        for element in self._elements:
            ret_val += element.render()

        return ret_val


class SequenceR(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    """
    Renders a sequence.

    Special name of the class to avoid clash with builtin name.
    """

    def __init__(self, elements: Sequence[Renderer[ELEMENT]]):
        self._elements = elements

    def render(self) -> Sequence[ELEMENT]:
        return [
            element.render()
            for element in self._elements
        ]


class SingletonSequenceR(Generic[ELEMENT], SequenceRenderer[ELEMENT]):
    """
    Renders a sequence.

    Special name of the class to avoid clash with builtin name.
    """

    def __init__(self, element: Renderer[ELEMENT]):
        self._element = element

    def render(self) -> Sequence[ELEMENT]:
        return [
            self._element.render()
        ]


class PrependFirstMinorBlockR(SequenceRenderer[MinorBlock]):
    def __init__(self,
                 to_prepend: Renderer[Sequence[LineElement]],
                 to_prepend_to: Renderer[Sequence[MinorBlock]],
                 properties_if_to_prepend_to_is_empty: ElementProperties =
                 structure.PLAIN_ELEMENT_PROPERTIES,
                 ):
        self.to_prepend = to_prepend
        self.to_prepend_to = to_prepend_to
        self.properties_if_to_prepend_to_is_empty = properties_if_to_prepend_to_is_empty

    def render(self) -> Sequence[MinorBlock]:
        to_prepend = self.to_prepend.render()
        to_prepend_to = self.to_prepend_to.render()

        if len(to_prepend) == 0:
            return to_prepend_to
        else:
            if len(to_prepend_to) == 0:
                return [
                    MinorBlock(to_prepend, self.properties_if_to_prepend_to_is_empty)
                ]
            else:
                to_prepend_to_list = list(to_prepend_to)
                original_first_block = to_prepend_to_list[0]
                line_elements = list(to_prepend)
                line_elements += original_first_block.parts
                to_prepend_to_list[0] = MinorBlock(line_elements,
                                                   original_first_block.properties)

                return to_prepend_to_list
