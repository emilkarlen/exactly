from typing import TypeVar, Sequence

from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import Element, Indentation

ELEMENT = TypeVar('ELEMENT', bound=Element)


class IncreasedIndentRenderer(SequenceRenderer[ELEMENT]):
    def __init__(self, renderer: SequenceRenderer[ELEMENT]):
        self._renderer = renderer

    def render_sequence(self) -> Sequence[ELEMENT]:
        ret_val = self._renderer.render_sequence()
        for element in ret_val:
            element.set_properties(element.properties.with_increased_indentation_level)

        return ret_val


class CustomIncreasedIndentRenderer(SequenceRenderer[ELEMENT]):
    def __init__(self,
                 renderer: SequenceRenderer[ELEMENT],
                 increase: Indentation,
                 ):
        self._renderer = renderer
        self._increase = increase

    def render_sequence(self) -> Sequence[ELEMENT]:
        ret_val = self._renderer.render_sequence()
        for element in ret_val:
            element.set_properties(element.properties.with_increased_indentation(self._increase))

        return ret_val
