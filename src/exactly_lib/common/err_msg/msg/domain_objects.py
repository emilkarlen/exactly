import pathlib

from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import line_objects, component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.structure import LineElement


def of_path(path: pathlib.Path) -> Renderer[LineElement]:
    return comp_rend.LineElementR(
        line_objects.PreFormattedString(path)
    )


def single_path(path: pathlib.Path) -> SequenceRenderer[LineElement]:
    return rend_comb.SingletonSequenceR(of_path(path))
