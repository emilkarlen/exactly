from typing import Sequence

from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.rendering import line_objects
from exactly_lib.util.simple_textstruct.structure import LineElement, LineObject


class SingleLineObject(SequenceRenderer[LineElement]):
    def __init__(self, line_object: Renderer[LineObject]):
        self._line_object = line_object

    def render_sequence(self) -> Sequence[LineElement]:
        return [
            LineElement(self._line_object.render())
        ]


def single_pre_formatted(s: str) -> SequenceRenderer[LineElement]:
    return SingleLineObject(line_objects.PreFormattedString(s))


def plain_sequence(line_renderers: Sequence[Renderer[LineObject]]) -> SequenceRenderer[LineElement]:
    return rend_comb.SequenceR([
        comp_rend.LineElementR(line_renderer)
        for line_renderer in line_renderers
    ])
