import pathlib
from typing import Sequence

from exactly_lib.util.simple_textstruct.rendering import line_objects, component_renderers as comp_rend, \
    renderer_combinators as rend_comb
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import LineElement


def of_path(path: pathlib.Path) -> Renderer[LineElement]:
    return comp_rend.LineElementR(
        line_objects.PreFormattedString(path)
    )


def single_path(path: pathlib.Path) -> Renderer[Sequence[LineElement]]:
    return rend_comb.SingletonSequenceR(of_path(path))
