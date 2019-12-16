from typing import Any

from exactly_lib.util import strings
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects
from exactly_lib.util.simple_textstruct.structure import MinorBlock, LineElement, MajorBlock
from exactly_lib.util.strings import ToStringObject

UNEXPECTED = 'Unexpected'


class SimpleHeaderMinorBlockRenderer(Renderer[MinorBlock]):
    def __init__(self, single_line_to_str: Any):
        self._single_line_to_str = single_line_to_str

    def render(self) -> MinorBlock:
        header = LineElement(text_struct.StringLineObject(str(self._single_line_to_str)))
        return MinorBlock(
            [header],
        )


def unexpected_attribute__major_block(attribute: ToStringObject) -> Renderer[MajorBlock]:
    return blocks.MajorBlockOfSingleLineObject(
        line_objects.StringLineObject(unexpected(attribute))
    )


def unexpected(attribute: ToStringObject) -> ToStringObject:
    return strings.Concatenate([
        UNEXPECTED,
        ' ',
        attribute,
    ],
    )
