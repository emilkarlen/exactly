from typing import Sequence

from exactly_lib.util.simple_textstruct.rendering import line_objects
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb, \
    component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.rendering.components import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import LineElement, LineObject


class SingleLineObject(SequenceRenderer[LineElement]):
    def __init__(self, line_object: Renderer[LineObject]):
        self._line_object = line_object

    def render(self) -> Sequence[LineElement]:
        return [
            LineElement(self._line_object.render())
        ]


def single_pre_formatted(s: str) -> Renderer[Sequence[LineElement]]:
    return SingleLineObject(line_objects.PreFormattedString(s))


def plain_sequence(line_renderers: Sequence[Renderer[LineObject]]) -> SequenceRenderer[LineElement]:
    return rend_comb.SequenceR([
        comp_rend.LineElementR(line_renderer)
        for line_renderer in line_renderers
    ])