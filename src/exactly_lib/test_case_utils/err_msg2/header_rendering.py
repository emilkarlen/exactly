from typing import Any

from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.structure import MinorBlock, LineElement


class SimpleHeaderMinorBlockRenderer(Renderer[MinorBlock]):
    def __init__(self, single_line_to_str: Any):
        self._single_line_to_str = single_line_to_str

    def render(self) -> MinorBlock:
        header = LineElement(text_struct.StringLineObject(str(self._single_line_to_str)))
        return MinorBlock(
            [header],
        )
