from typing import Sequence

from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.rendering.components import LineObjectRenderer
from exactly_lib.util.simple_textstruct.structure import MinorBlock, LineElement, MajorBlock


class MinorBlockOfSingleLineObject(Renderer[MinorBlock]):
    def __init__(self, line_object_renderer: LineObjectRenderer):
        self._line_object_renderer = line_object_renderer

    def render(self) -> MinorBlock:
        renderer = comp_rend.MinorBlockR(
            rend_comb.SingletonSequenceR(
                comp_rend.LineElementR(self._line_object_renderer)
            )
        )
        return renderer.render()


class MinorBlocksOfSingleLineObject(SequenceRenderer[MinorBlock]):
    def __init__(self, line_object_renderer: LineObjectRenderer):
        self._line_object_renderer = line_object_renderer

    def render_sequence(self) -> Sequence[MinorBlock]:
        renderer = rend_comb.SingletonSequenceR(
            MinorBlockOfSingleLineObject(self._line_object_renderer)
        )
        return renderer.render_sequence()


class MinorBlocksOfLineElements(SequenceRenderer[MinorBlock]):
    def __init__(self, line_elements_renderer: SequenceRenderer[LineElement]):
        self._line_elements_renderer = line_elements_renderer

    def render_sequence(self) -> Sequence[MinorBlock]:
        renderer = rend_comb.SingletonSequenceR(
            comp_rend.MinorBlockR(self._line_elements_renderer)
        )
        return renderer.render()


def major_block_of_single_minor_block(minor_block: Renderer[MinorBlock]) -> Renderer[MajorBlock]:
    return comp_rend.MajorBlockR(
        rend_comb.SingletonSequenceR(minor_block)
    )


class MajorBlockOfSingleLineObject(Renderer[MajorBlock]):
    def __init__(self, line_object_renderer: LineObjectRenderer):
        self._line_object_renderer = line_object_renderer

    def render(self) -> MajorBlock:
        renderer = major_block_of_single_minor_block(
            MinorBlockOfSingleLineObject(self._line_object_renderer)
        )
        return renderer.render()


class MajorBlocksOfSingleLineObject(SequenceRenderer[MajorBlock]):
    def __init__(self, line_object_renderer: LineObjectRenderer):
        self._line_object_renderer = line_object_renderer

    def render_sequence(self) -> Sequence[MajorBlock]:
        renderer = rend_comb.SingletonSequenceR(
            MajorBlockOfSingleLineObject(self._line_object_renderer)
        )
        return renderer.render_sequence()


class MajorBlocksOfLineElements(SequenceRenderer[MajorBlock]):
    def __init__(self, line_elements_renderer: SequenceRenderer[LineElement]):
        self._line_elements_renderer = line_elements_renderer

    def render_sequence(self) -> Sequence[MajorBlock]:
        renderer = rend_comb.SingletonSequenceR(
            comp_rend.MajorBlockR(MinorBlocksOfLineElements(self._line_elements_renderer))
        )
        return renderer.render()
