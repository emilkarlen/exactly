from typing import Sequence

from exactly_lib.util.simple_textstruct.rendering import line_objects
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


def of_pre_formatted(s: str) -> Renderer[LineElement]:
    return SingleLineObject(line_objects.PreFormattedString(s))
